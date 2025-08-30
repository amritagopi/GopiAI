import os
import json
from pathlib import Path
from typing import Any, Dict

APP_FOLDER_NAME = "GopiAI"
SETTINGS_FILENAME = "settings.json"


def get_settings_candidates() -> list[Path]:
    candidates: list[Path] = []
    # 1) Explicit path
    custom = os.getenv("GOPIAI_SETTINGS_PATH")
    if custom:
        p = Path(custom)
        if p.is_file():
            candidates.append(p)
        elif p.is_dir():
            candidates.extend([p / SETTINGS_FILENAME, p / "config" / SETTINGS_FILENAME])
    # 2) CWD
    cwd = Path.cwd()
    candidates.extend([cwd / SETTINGS_FILENAME, cwd / "config" / SETTINGS_FILENAME])
    # 3) Module dir
    here = Path(__file__).resolve().parent
    candidates.extend([here / SETTINGS_FILENAME, here / "config" / SETTINGS_FILENAME])
    # 4) APPDATA
    appdata = os.getenv("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / APP_FOLDER_NAME / SETTINGS_FILENAME)
    return candidates


def get_primary_settings_path(create_dirs: bool = False) -> Path:
    """Primary writable location: %APPDATA%/GopiAI/settings.json (Windows),
    else ./settings.json."""
    appdata = os.getenv("APPDATA")
    if appdata:
        base = Path(appdata) / APP_FOLDER_NAME
        if create_dirs:
            base.mkdir(parents=True, exist_ok=True)
        return base / SETTINGS_FILENAME
    # Fallback to CWD
    base = Path.cwd()
    if create_dirs:
        base.mkdir(parents=True, exist_ok=True)
    return base / SETTINGS_FILENAME


def read_settings() -> Dict[str, Any]:
    for p in get_settings_candidates():
        try:
            if p.is_file():
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            continue
    return {}


def write_settings(data: Dict[str, Any]) -> Path:
    path = get_primary_settings_path(create_dirs=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path
    except Exception as e:
        raise RuntimeError(f"Не удалось записать settings.json: {e}")


def set_terminal_unsafe(enabled: bool) -> Path:
    data = read_settings()
    data["terminal_unsafe"] = bool(enabled)
    return write_settings(data)
