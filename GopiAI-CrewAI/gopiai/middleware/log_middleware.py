import time

from fastapi import Request
from starlette.types import ASGIApp

from gopiai.logging.json_logger import jlog, ensure_request_id


class LoggingMiddleware:
    """
    FastAPI/Starlette middleware:
    - ensures X-Request-ID
    - logs request_in, request_out, error with latency_ms and success
    Aligned with DeerFlow logging standard.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        start = time.time()

        # request id
        req_id = ensure_request_id(request.headers.get("X-Request-ID"))
        # propagate for downstream handlers
        scope.setdefault("state", {})
        request.state.request_id = req_id

        # request_in
        try:
            jlog(
                level="INFO",
                event="request_in",
                request_id=req_id,
                route=str(request.url),
                method=request.method,
            )
        except Exception:
            # avoid breaking the request flow due to logging issue
            pass

        # wrapper to capture response status
        status_code_holder = {"status": 500}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code_holder["status"] = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
            latency = int((time.time() - start) * 1000)
            jlog(
                level="INFO",
                event="request_out",
                request_id=req_id,
                route=str(request.url),
                method=request.method,
                status_code=status_code_holder["status"],
                latency_ms=latency,
                success=200 <= status_code_holder["status"] < 400,
            )
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            jlog(
                level="ERROR",
                event="error",
                request_id=req_id,
                route=str(request.url),
                method=request.method,
                error_message=str(e),
                latency_ms=latency,
                success=False,
            )
            raise


# FastAPI helper to add middleware explicitly in app factory.
def setup_logging_middleware(app) -> None:
    """
    app.add_middleware(LoggingMiddleware)
    """
    app.add_middleware(LoggingMiddleware)
