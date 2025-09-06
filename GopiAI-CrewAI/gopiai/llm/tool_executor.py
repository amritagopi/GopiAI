from __future__ import annotations
from typing import Any, Callable, Dict

from gopiai.logging.json_logger import jlog, now_ms


class ToolExecutor:
    """
    Простая обертка-исполнитель инструментов с логированием DeerFlow:
    - event=tool_call при старте
    - event=tool_result по завершении, latency_ms и краткая мета-информация результата
    """

    def __init__(self, registry: Dict[str, Callable[..., Any]]):
        self.registry = registry

    def execute(self, request_id: str, tool_name: str, **kwargs) -> Any:
        if tool_name not in self.registry:
            jlog(
                level="ERROR",
                event="tool_call",
                request_id=request_id,
                tool_name=tool_name,
                error_message="Unknown tool",
                success=False,
            )
            raise ValueError(f"Unknown tool '{tool_name}'")

        func = self.registry[tool_name]
        start = now_ms()
        jlog(
            level="INFO",
            event="tool_call",
            request_id=request_id,
            tool_name=tool_name,
            tool_args_keys=list(kwargs.keys()),
            start_ms=start,
        )
        try:
            result = func(**kwargs)
            latency = now_ms() - start
            # короткая сводка результата (без чувствительных данных)
            meta = _summarize_result(result)
            jlog(
                level="INFO",
                event="tool_result",
                request_id=request_id,
                tool_name=tool_name,
                latency_ms=latency,
                tool_result_meta=meta,
                success=True,
            )
            return result
        except Exception as e:
            latency = now_ms() - start
            jlog(
                level="ERROR",
                event="tool_result",
                request_id=request_id,
                tool_name=tool_name,
                latency_ms=latency,
                error_message=str(e),
                success=False,
            )
            raise


def _summarize_result(result: Any) -> Dict[str, Any]:
    try:
        if result is None:
            return {"type": "none"}
        if isinstance(result, (str, bytes)):
            length = len(result)
            return {"type": "text", "length": length}
        if isinstance(result, (list, tuple, set)):
            return {"type": "sequence", "len": len(result)}
        if isinstance(result, dict):
            return {"type": "dict", "keys": list(result.keys())[:10]}
        return {"type": type(result).__name__}
    except Exception:
        return {"type": "unknown"}
