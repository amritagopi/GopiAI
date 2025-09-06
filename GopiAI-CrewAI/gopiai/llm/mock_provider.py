from __future__ import annotations

import time
from typing import Any, Dict, List

from gopiai.logging.json_logger import jlog, now_ms
from .tool_spec import ToolSpec


class MockProvider:
    """
    Мок-провайдер для тестов DeerFlow.

    Поведение:
    - Для openai: имитирует tool_calls в стиле OpenAI (function calling).
    - Для google (Gemini): имитирует functionCall цикл.

    Это позволяет юнит-тестам проверять корректность сериализации tools и обработку
    различных стилей провайдеров без реальных сетевых вызовов.
    """

    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model

    def chat(self, messages: List[Dict[str, Any]], tools: List[ToolSpec] | None = None, **kwargs) -> Dict[str, Any]:
        start = now_ms()
        jlog(
            level="INFO",
            event="llm_request",
            provider=self.provider,
            model=self.model,
            tool_names=[t.name for t in (tools or [])],
            params={k: v for k, v in kwargs.items() if k in ("temperature", "top_p", "tool_choice")},
        )
        # имитация небольшой латентности
        time.sleep(0.01)

        if (self.provider or "").lower() in ("openai",):
            # Вернём ответ, который сообщает о функции, которую "решила" вызвать модель
            resp = {
                "id": "mock-openai-chatcmpl",
                "object": "chat.completion",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "tool_calls",
                        "message": {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "type": "function",
                                    "function": {
                                        "name": (tools[0].name if tools else "no_tool"),
                                        "arguments": '{"query": "test"}',
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
            jlog(
                level="INFO",
                event="llm_response",
                provider=self.provider,
                model=self.model,
                provider_latency_ms=now_ms() - start,
                finish_reason="tool_calls",
                tool_call_count=1,
                tool_calls=[(tools[0].name if tools else "no_tool")],
            )
            return resp

        if (self.provider or "").lower() == "google":
            # Gemini-style: функция и её аргументы через functionCall
            resp = {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "functionCall": {
                                        "name": (tools[0].name if tools else "no_tool"),
                                        "args": {"query": "test"},
                                    }
                                }
                            ]
                        },
                        "finishReason": "STOP",
                    }
                ]
            }
            jlog(
                level="INFO",
                event="llm_response",
                provider=self.provider,
                model=self.model,
                provider_latency_ms=now_ms() - start,
                finish_reason="functionCall",
                tool_call_count=1,
                tool_calls=[(tools[0].name if tools else "no_tool")],
            )
            return resp

        raise ValueError(f"Unknown provider '{self.provider}'")
