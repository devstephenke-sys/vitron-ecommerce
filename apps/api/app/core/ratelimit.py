"""In-memory sliding-window rate limiter for abuse-prone endpoints.

Scope: per (scope, client IP) fixed-window counters held in process
memory. This is intentionally simple for Phase 2 — it protects a single
API instance and resets on restart. Move to a shared store (Redis or a
database table) before running multiple replicas; tracked as a residual
risk in docs/10-decisions-and-risks.md.
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


class RateLimiter:
    """Sliding-window counter keyed by an arbitrary string."""

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, limit: int, window_seconds: float) -> None:
        """Raise 429 when `key` exceeds `limit` hits within the window."""
        now = time.monotonic()
        hits = self._hits[key]
        while hits and now - hits[0] > window_seconds:
            hits.popleft()
        if len(hits) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
                headers={"Retry-After": str(int(window_seconds))},
            )
        hits.append(now)
        # Opportunistic cleanup so the map cannot grow without bound.
        if len(self._hits) > 10_000:
            self._sweep(now)

    def reset(self) -> None:
        """Clear all counters (test isolation)."""
        self._hits.clear()

    def _sweep(self, now: float) -> None:
        stale_window = 3600.0
        for key in [k for k, v in self._hits.items() if not v or now - v[-1] > stale_window]:
            del self._hits[key]


_limiter = RateLimiter()


def rate_limit(scope: str, limit: int, window_seconds: float = 60.0):
    """FastAPI dependency factory: rate-limit by client IP + scope."""

    async def _dependency(request: Request) -> None:
        client = request.client.host if request.client else "unknown"
        _limiter.check(f"{scope}:{client}", limit, window_seconds)

    return _dependency
