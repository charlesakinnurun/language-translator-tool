"""ASGI middleware: request correlation IDs, access logging, rate limiting."""

import logging
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.rate_limit import SlidingWindowRateLimiter, client_key

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a correlation ID, log access events and timing per request."""

    async def dispatch(self, request: Request, call_next):
        request_id = uuid.uuid4().hex[:12]
        request.state.request_id = request_id

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "unhandled_exception",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            raise
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "http_request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )
        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests that exceed the per-client sliding-window budget."""

    def __init__(
        self,
        app,
        limiter: SlidingWindowRateLimiter | None,
        enabled: bool = True,
    ) -> None:
        super().__init__(app)
        self._limiter = limiter
        self._enabled = enabled

    async def dispatch(self, request: Request, call_next):
        if self._enabled and self._limiter is not None:
            if not self._limiter.is_allowed(client_key(request)):
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": {
                            "code": "rate_limited",
                            "message": (
                                "Too many requests. Please wait a moment and try again."
                            ),
                        }
                    },
                    headers={"Retry-After": str(self._limiter.window_seconds)},
                )
        return await call_next(request)