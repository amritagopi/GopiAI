from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class ProviderClient:
    """
    Lightweight client/config holder for an LLM provider.
    Stores endpoint, headers (masked externally), and provider name.
    """
    provider: str
    endpoint: str
    headers: Dict[str, str]
    created_at_ms: int


def _now_ms() -> int:
    return int(time.time() * 1000)


def _mask(s: Optional[str]) -> str:
    if not s:
        return ""
    return s[:4] + "***" + s[-3:] if len(s) > 10 else "***"


def get_api_key(provider: str) -> Optional[str]:
    """
    Read API key from environment each time (no sticky globals).
    """
    p = (provider or "").lower()
    if p == "openai":
        return os.getenv("OPENAI_API_KEY")
    if p == "google":
        return os.getenv("GOOGLE_API_KEY")
    return None


def _endpoint_for(provider: str) -> str:
    p = (provider or "").lower()
    if p == "openai":
        return os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1/chat/completions")
    if p == "google":
        return os.getenv("GOOGLE_ENDPOINT", "https://generativelanguage.googleapis.com")
    raise ValueError(f"Unknown provider '{provider}'")


def _auth_header_for(provider: str, api_key: Optional[str]) -> Dict[str, str]:
    p = (provider or "").lower()
    if not api_key:
        return {}
    if p == "openai":
        return {"Authorization": f"Bearer {api_key}"}
    if p == "google":
        # Gemini uses key in query typically, but some SDKs accept header as well
        return {"x-goog-api-key": api_key}
    return {}


def _hash_effective_config(effective_cfg_no_secrets: Dict[str, Any]) -> str:
    """
    Create a stable hash for effective configuration without secrets.
    """
    import json
    data = json.dumps(effective_cfg_no_secrets, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]


# Simple LRU with TTL for ProviderClient keyed by (provider, effective_config_hash)
_CACHE: Dict[Tuple[str, str], Tuple[ProviderClient, int]] = {}
_CACHE_TTL_SEC = int(os.getenv("PROVIDER_CLIENT_TTL_SEC", "60"))


def _purge_expired() -> None:
    if not _CACHE:
        return
    now = int(time.time())
    expired = [k for k, (_, ts) in _CACHE.items() if now - ts > _CACHE_TTL_SEC]
    for k in expired:
        _CACHE.pop(k, None)


def build_client(provider: str, effective_cfg_no_secrets: Dict[str, Any]) -> Tuple[ProviderClient, str]:
    """
    Build a provider client per request (or reuse from short TTL cache).
    Returns (client, effective_config_hash).
    """
    _purge_expired()
    eff_hash = _hash_effective_config(effective_cfg_no_secrets)
    cache_key = ((provider or "").lower(), eff_hash)
    cached = _CACHE.get(cache_key)
    if cached:
        client, _ = cached
        return client, eff_hash

    api_key = get_api_key(provider)
    endpoint = _endpoint_for(provider)
    headers = {
        "Content-Type": "application/json",
        **_auth_header_for(provider, api_key),
    }
    client = ProviderClient(
        provider=(provider or "").lower(),
        endpoint=endpoint,
        headers=headers,
        created_at_ms=_now_ms(),
    )
    _CACHE[cache_key] = (client, int(time.time()))
    return client, eff_hash
