"""Unified LLM rotation config for GopiAI back-end.

Key features
------------
1. Support two providers out of the box: Google Gemini and OpenRouter.
2. All model metadata lives in a single `MODELS` list; each item contains
   provider, id, human-readable name, supported task types and optional
   extra params (rpm, tpm, rpd, base_score).
3. Key map is centralised in `PROVIDER_KEY_ENV`; helper
   `get_api_key_for_provider()` always works.
4. One `UsageTracker` to record rpm/tpm/rpd usage **per model** – no more
   scattered dicts.
5. Convenience helpers: `get_available_models`, `get_next_available_model`,
   `register_use`, `mark_unavailable`, `get_model_usage_stats`.
6. State synchronization with ~/.gopiai_state.json
7. Soft blacklist implementation for rate limiting violations
8. API key validation

This module aims to be drop-in compatible with existing import points
(`from gopiai_integration.llm_rotation_config import ...`).  If your code
relies on removed helper functions – import them from here or migrate.
"""
from __future__ import annotations

import base64
import os
import time
import re
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

###############################################################################
# Provider –> env variable map
###############################################################################
PROVIDER_KEY_ENV: dict[str, str] = {
    "gemini": "GEMINI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

###############################################################################
# Model catalogue
###############################################################################

MODELS: list[dict] = [
    # Google Gemini
    {
        "display_name": "Gemini 1.5 Flash",
        "id": "gemini/gemini-1.5-flash",
        "provider": "gemini",
        "rpm": 15,
        "tpm": 2_500_000,
        "type": ["simple", "dialog", "code", "summarize"],
        "priority": 3,
        "rpd": 50,
        "base_score": 0.5,
    },
    {
        "display_name": "Gemini 2.0 Flash-Lite",
        "id": "gemini/gemini-2.0-flash-lite",
        "provider": "gemini",
        "rpm": 30,
        "tpm": 10_000_000,
        "type": ["simple", "dialog", "code", "summarize"],
        "priority": 4,
        "rpd": 200,
        "base_score": 0.5,
    },
    {
        "display_name": "Gemini 3",
        "id": "gemini/gemini-3",
        "provider": "gemini",
        "rpm": 30,
        "tpm": 1_440_000,
        "type": ["simple", "lookup", "short_answer"],
        "priority": 1,
        "rpd": 0,
        "base_score": 0.5,
    },
    # ---------------------- OpenRouter block ----------------------
    {
        "display_name": "Venice: Uncensored (free)",
        "id": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        "provider": "openrouter",
        "rpm": 20,
        "tpm": 2_000_000,
        "type": ["dialog", "simple", "code", "summarize"],
        "priority": 1,
        "rpd": 100,
        "base_score": 0.8,
    },
    {
        "display_name": "DeepSeek R1 Distill Qwen 14B (free)",
        "id": "deepseek/deepseek-r1-distill-qwen-14b:free",
        "provider": "openrouter",
        "rpm": 15,
        "tpm": 1_500_000,
        "type": ["dialog", "simple", "code"],
        "priority": 2,
        "rpd": 80,
        "base_score": 0.7,
    },
    {
        "display_name": "Dolphin3.0 Mistral 24B (free)",
        "id": "cognitivecomputations/dolphin3.0-mistral-24b:free",
        "provider": "openrouter",
        "rpm": 18,
        "tpm": 1_800_000,
        "type": ["dialog", "simple", "code"],
        "priority": 2,
        "rpd": 90,
        "base_score": 0.6,
    },
    {
        "display_name": "Qwen 3 Coder (OpenRouter)",
        "id": "qwen/qwen3-coder:free",
        "provider": "openrouter",
        "rpm": 20,
        "tpm": 2_000_000,
        "type": ["simple", "code"],
        "priority": 3,
        "rpd": 100,
        "base_score": 0.4,
    },
    {
        "display_name": "Gemini 2.0 Flash-Exp (OpenRouter)",
        "id": "google/gemini-2.0-flash-exp:free",
        "provider": "openrouter",
        "rpm": 10,
        "tpm": 4_000_000,
        "type": ["dialog", "summarize", "code"],
        "priority": 4,
        "rpd": 100,
        "base_score": 0.3,
    },
    # Локальные модели (без API ключей)
    {
        "display_name": "TinyLlama 1.1B (local)",
        "id": "local/tinyllama-1.1b",
        "provider": "local",
        "rpm": 5,
        "tpm": 1000,
        "type": ["simple", "dialog", "code"],
        "priority": 5,
        "rpd": 0,
        "base_score": 0.4,
        "local_model": True,
        "model_path": "TheBloke/TinyLlama-1.1B-Chat-v0.3-GGUF/tinyllama-1.1b-chat-v0.3.Q2_K.gguf"
    }
]

###############################################################################
# Usage tracker
###############################################################################

@dataclass
class _ModelUsage:
    rpm: int = 0  # requests per minute used in current window
    tpm: int = 0  # tokens per minute used in current window
    rpd: int = 0  # requests per day used (reset at midnight)
    last_reset: float = field(default_factory=time.time)
    # Для мягкого черного списка
    last_rpm_check: float = field(default_factory=time.time)
    rpm_violations: int = 0
    blacklisted_until: float = 0  # timestamp когда модель будет разблокирована

class UsageTracker:
    """Keeps request/token counts for each model & cleans stale windows."""

    def __init__(self, models: list[dict]):
        # model_id -> usage struct
        self._usage: Dict[str, _ModelUsage] = {
            m["id"]: _ModelUsage() for m in models
        }
        self._current_provider: str = "gemini"  # текущий провайдер
        self._last_provider: str = "gemini"     # последний провайдер

    def set_current_provider(self, provider: str) -> None:
        """Устанавливает текущий провайдер и сбрасывает лимиты для других провайдеров."""
        if provider not in PROVIDER_KEY_ENV:
            raise ValueError(f"Unknown provider: {provider}")
            
        self._last_provider = self._current_provider
        self._current_provider = provider
        
        # Сбрасываем окна лимитов для моделей, принадлежащих другим провайдерам
        now = time.time()
        for model_id, usage in self._usage.items():
            # Находим модель в MODELS по ID
            model_cfg = next((m for m in MODELS if m["id"] == model_id), None)
            if model_cfg and model_cfg["provider"] != provider:
                # Сбрасываем лимиты для моделей других провайдеров
                usage.rpm = 0
                usage.tpm = 0
                usage.last_reset = now

    # ---------------------------------------------------------------------
    # internal helpers
    # ---------------------------------------------------------------------
    def _maybe_reset_minute(self, model_id: str) -> None:
        usage = self._usage[model_id]
        now = time.time()
        if now - usage.last_reset > 60:  # reset every minute
            usage.rpm = 0
            usage.tpm = 0
            usage.last_reset = now

    def _maybe_reset_day(self, model_id: str) -> None:
        usage = self._usage[model_id]
        now = time.time()
        if now - usage.last_reset > 86_400:  # 24h
            usage.rpd = 0
            usage.last_reset = now

    def _check_blacklist(self, model_id: str) -> bool:
        """Проверяет, заблокирована ли модель в черном списке."""
        usage = self._usage[model_id]
        now = time.time()
        
        # Если время блокировки прошло, разблокируем модель
        if usage.blacklisted_until > 0 and now >= usage.blacklisted_until:
            usage.blacklisted_until = 0
            usage.rpm_violations = 0  # Сбрасываем нарушения при разблокировке
            return False
            
        # Если модель заблокирована, возвращаем True
        return usage.blacklisted_until > 0

    # ---------------------------------------------------------------------
    # public API
    # ---------------------------------------------------------------------
    def can_use(self, model_cfg: dict, tokens: int = 0) -> bool:
        mid = model_cfg["id"]
        self._maybe_reset_minute(mid)
        self._maybe_reset_day(mid)
        
        # Проверяем черный список
        if self._check_blacklist(mid):
            logger.warning(f"❌ Модель {mid} заблокирована в черном списке (осталось: {self._usage[mid].blacklisted_until - time.time():.1f} сек)")
            return False
            
        usage = self._usage[mid]
        can_use = (
            usage.rpm < model_cfg["rpm"]
            and usage.tpm + tokens < model_cfg["tpm"]
            and usage.rpd < model_cfg["rpd"]
        )
        
        if not can_use:
            reasons = []
            if usage.rpm >= model_cfg["rpm"]:
                reasons.append(f"RPM лимит: {usage.rpm}/{model_cfg['rpm']}")
            if usage.tpm + tokens >= model_cfg["tpm"]:
                reasons.append(f"TPM лимит: {usage.tpm + tokens}/{model_cfg['tpm']}")
            if usage.rpd >= model_cfg["rpd"]:
                reasons.append(f"RPD лимит: {usage.rpd}/{model_cfg['rpd']}")
            logger.warning(f"❌ Модель {mid} недоступна: {', '.join(reasons)}")
            
        return can_use

    def register_use(self, model_cfg: dict, tokens: int = 0) -> None:
        mid = model_cfg["id"]
        self._maybe_reset_minute(mid)
        self._maybe_reset_day(mid)
        usage = self._usage[mid]
        usage.rpm += 1
        usage.tpm += tokens
        usage.rpd += 1
        
        # Проверяем превышение RPM для мягкого черного списка
        now = time.time()
        if usage.rpm > model_cfg["rpm"] * 1.5:  # Превышение лимита на 50%
            usage.rpm_violations += 1
            
            # Если это первое нарушение, блокируем модель
            if usage.rpm_violations == 1:
                # Блокировка на N секунд, где N = 60 / rpm_limit
                block_duration = 60.0 / model_cfg["rpm"]
                usage.blacklisted_until = now + block_duration
                logger.warning(f"🔒 Модель {mid} заблокирована на {block_duration:.1f} сек из-за превышения RPM (текущий: {usage.rpm}, лимит: {model_cfg['rpm']})")

    def get_stats(self, model_id: str) -> dict:
        u = self._usage[model_id]
        now = time.time()
        return {
            "rpm": u.rpm, 
            "tpm": u.tpm, 
            "rpd": u.rpd,
            "blacklisted": u.blacklisted_until > now if u.blacklisted_until > 0 else False,
            "blacklisted_until": u.blacklisted_until if u.blacklisted_until > 0 else 0,
            "rpm_violations": u.rpm_violations
        }

    def is_blacklisted(self, model_id: str) -> bool:
        """Проверяет, находится ли модель в черном списке."""
        return self._check_blacklist(model_id)

    # Legacy compatibility helpers expected by older ai_router code
    def get_blacklist_status(self) -> dict:
        """Return model_id -> seconds until unblocked."""
        now = time.time()
        result = {}
        for model_id, usage in self._usage.items():
            if usage.blacklisted_until > now:
                result[model_id] = usage.blacklisted_until - now
        return result

    @property
    def models(self):
        """Expose catalogue for legacy access (read-only)."""
        return MODELS

    @property
    def current_provider(self) -> str:
        """Возвращает текущий провайдер."""
        return self._current_provider

###############################################################################
# Global tracker instance
###############################################################################

_usage_tracker = UsageTracker(MODELS)

#############################################
# Load persisted state (provider/model)
#############################################
try:
    from .state_manager import load_state, save_state  # type: ignore
except ImportError:
    # when imported from other packages relative path may fail
    from state_manager import load_state, save_state  # type: ignore

_state = load_state()
_current_provider = _state.get("provider", "gemini")
_current_model = _state.get("model_id", "")

# expose helpers for other modules/UI
CURRENT_PROVIDER = _current_provider
CURRENT_MODEL_ID = _current_model

def update_state(provider: str, model_id: str):
    """Persist new provider/model choice to state file."""
    global CURRENT_PROVIDER, CURRENT_MODEL_ID
    CURRENT_PROVIDER = provider
    CURRENT_MODEL_ID = model_id
    save_state(provider, model_id)
    # Обновляем текущий провайдер в tracker
    _usage_tracker.set_current_provider(provider)

# init tracker current provider (basic reset logic)
_usage_tracker.set_current_provider(_current_provider)  # type: ignore


###############################################################################
# Convenience helpers
###############################################################################

def get_api_key_for_provider(provider: str) -> Optional[str]:
    """Return API key for given provider or None if missing."""
    env_name = PROVIDER_KEY_ENV.get(provider.lower())
    if not env_name:
        return None
    key = os.getenv(env_name)
    
    # Валидация ключа
    if key:
        key = key.strip()
        # Проверяем, что ключ не пустой и имеет разумную длину
        if len(key) < 20:
            print(f"[WARNING] API key for {provider} appears to be too short")
        if ' ' in key:
            print(f"[WARNING] API key for {provider} contains spaces")
        return key if key else None
    return None


def get_available_models(task_type: str) -> List[dict]:
    """Return list of *enabled & non-saturated* models supporting task_type."""
    result: list[dict] = []
    for m in MODELS:
        if task_type in m["type"] and get_api_key_for_provider(m["provider"]):
            if _usage_tracker.can_use(m):
                result.append(m)
    # sort by provider priority first, then base_score
    result.sort(key=lambda m: (m["priority"], -m.get("base_score", 0)))
    return result


def get_next_available_model(task_type: str, tokens: int = 0) -> Optional[dict]:
    """Return first usable model for task OR None."""
    for m in get_available_models(task_type):
        if _usage_tracker.can_use(m, tokens):
            return m
    return None


def register_use(model_id: str, tokens: int = 0) -> None:
    m = next((x for x in MODELS if x["id"] == model_id), None)
    if m:
        _usage_tracker.register_use(m, tokens)


def get_model_usage_stats(model_id: str) -> dict:
    return _usage_tracker.get_stats(model_id)


def is_model_blacklisted(model_id: str) -> bool:
    """Проверяет, заблокирована ли модель."""
    return _usage_tracker.is_blacklisted(model_id)


def get_current_provider() -> str:
    """Возвращает текущий провайдер."""
    return _usage_tracker.current_provider


###############################################################################
# Backwards-compat shims (minimal subset)
###############################################################################

RateLimitMonitor = UsageTracker  # old alias
rate_limit_monitor = _usage_tracker  # legacy lowercase symbol
usage_tracker = _usage_tracker  # export for server imports
LLM_MODELS_CONFIG = MODELS  # historical constant expected by ai_router_llm

def get_models_by_intelligence(min_score: float = 0.0):
    """Legacy helper returning models with base_score >= min_score."""
    return [m for m in MODELS if m.get("base_score", 0) >= min_score]


# Legacy functions expected elsewhere
def select_llm_model_safe(task_type: str = "dialog", tokens: int = 0, intelligence_priority: bool = False):
    """Legacy helper: return first available model and register its usage.
    Keeps API surface for old ai_router_llm import.
    """
    model = get_next_available_model(task_type, tokens)
    if model:
        register_use(model["id"], tokens)
    return model

print("[INFO] llm_rotation_config loaded – providers:", \
      {p: PROVIDER_KEY_ENV[p] for p in PROVIDER_KEY_ENV})