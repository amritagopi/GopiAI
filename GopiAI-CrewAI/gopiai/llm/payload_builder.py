from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .tool_spec import ToolSpec, to_openai_tools, to_gemini_tools


def build_payload(
    provider: str,
    model: str,
    messages: List[Dict[str, Any]],
    tools: Optional[List[ToolSpec]],
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    tool_choice: Optional[str] = "auto",
) -> Dict[str, Any]:
    """
    Build provider-specific payload according to DeerFlow standard adapter.

    - For openai:
      {"model": ..., "messages": ..., "tools": [...], "tool_choice": ..., "temperature": ..., "top_p": ...}
    - For google (Gemini):
      {"model": ..., "contents": ..., "tools": {"function_declarations":[...]}, "generationConfig": {...}}
    """
    provider_norm = (provider or "").lower()
    temperature = temperature if temperature is not None else _default_float("TEMPERATURE_DEFAULT", 0.2)
    top_p = top_p if top_p is not None else _default_float("TOP_P_DEFAULT", 0.95)

    if provider_norm == "openai":
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
        }
        if tools:
            payload["tools"] = to_openai_tools(tools)
            payload["tool_choice"] = tool_choice or "auto"
        return payload

    if provider_norm == "google":
        payload = {
            "model": model,
            "contents": messages,
            "tools": to_gemini_tools(tools or []),
            "generationConfig": {
                "temperature": temperature,
                "topP": top_p,
            },
        }
        return payload

    raise ValueError(f"Unknown provider '{provider}'")


def _default_float(env_key: str, fallback: float) -> float:
    try:
        val = os.getenv(env_key)
        if val is None:
            return fallback
        return float(val)
    except Exception:
        return fallback
