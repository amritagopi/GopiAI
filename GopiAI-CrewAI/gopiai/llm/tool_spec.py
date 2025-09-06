from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema for OpenAI or OpenAPI-like for Gemini


def to_openai_tools(tools: List[ToolSpec]) -> List[Dict[str, Any]]:
    """
    OpenAI format:
    [{"type":"function","function":{"name":..., "description":..., "parameters": {...}}}]
    """
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            },
        }
        for t in tools
    ]


def to_gemini_tools(tools: List[ToolSpec]) -> Dict[str, Any]:
    """
    Gemini format:
    {"function_declarations":[{"name":..., "description":..., "parameters": {...}}, ...]}
    """
    return {
        "function_declarations": [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            }
            for t in tools
        ]
    }
