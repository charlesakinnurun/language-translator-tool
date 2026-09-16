"""Simple, dependency-free, in-process sliding-window rate limiter.

Suitable for single-instance deployments. Swap this for a shared store such
as Redis when scaling to multiple instances (see README "Future
Improvements").
"""

import threading
import time
from collections import defaultdict, deque


class SlidingWindowRateLimiter:
    """Tracks request timestamps per client key within a rolling window."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        if max_requests <= 0 or window_seconds <= 0:
            raise ValueError("max_requests and window_seconds must be positive")
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    @property
    def window_seconds(self) -> int:
        return self._window_seconds

    def is_allowed(self, key: str) -> bool:
        """Record a hit for ``key`` and answer whether it is within budget."""
        with self._lock:
            now = time.monotonic()
            window = self._hits[key]
            while window and now - window[0] > self._window_seconds:
                window.popleft()
            if len(window) >= self._max_requests:
                return False
            window.append(now)
            return True


def client_key(request) -> str:
    """Best-effort client identifier, honouring reverse-proxy forwarding."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"