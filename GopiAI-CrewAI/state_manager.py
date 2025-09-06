"""Simple state manager to persist current provider/model across app restarts.
File path is resolved to user's home directory: ~/.gopiai_state.json
"""
from __future__ import annotations

import json
from pathlib import Path

# Храним состояние в $HOME/.gopiai/state.json, гарантируем наличие каталога
STATE_DIR = Path.home() / ".gopiai"
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_PATH = STATE_DIR / "state.json"

_DEFAULT_STATE = {"provider": "gemini", "model_id": ""}


def load_state() -> dict:
    """Return dict with keys provider, model_id.  If file missing → defaults."""
    if STATE_PATH.exists():
        try:
            with STATE_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
            # Ensure required keys
            if not all(k in data for k in ("provider", "model_id")):
                raise ValueError("Bad state format")
            return data
        except Exception as exc:  # pragma: no cover
            print(f"[WARN] state_manager.load_state: {exc}. Using defaults.")
    else:
        # Пытаемся мигрировать из старого расположения ~/.gopiai_state.json
        legacy = Path.home() / ".gopiai_state.json"
        if legacy.exists():
            try:
                with legacy.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                # ensure dir
                STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
                STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"[INFO] Migrated legacy state from {legacy} to {STATE_PATH}")
                return data
            except Exception as exc:  # pragma: no cover
                print(f"[WARN] Failed to migrate legacy state: {exc}. Using defaults.")
    return _DEFAULT_STATE.copy()


def save_state(provider: str, model_id: str) -> None:
    """Persist provider/model_id to STATE_PATH (mkdir if needed)."""
    data = {"provider": provider, "model_id": model_id}
    try:
        # ensure parent dir exists
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] state_manager.save_state: {exc}")


def get_state_path() -> Path:
    return STATE_PATH
