"""HTTP middleware: request ID propagation and access logging."""

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger, new_request_id, request_id_var

logger = get_logger("vitron.access")

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Ensure every request has a correlation ID.

    Accepts an inbound ``X-Request-ID`` header when present (for upstream
    proxies) and always returns the effective ID on the response.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or new_request_id()
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "%s %s -> %s %.1fms",
                request.method,
                request.url.path,
                getattr(response, "status_code", 500),
                duration_ms,
            )
            request_id_var.reset(token)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def new_request_id_value() -> str:
    return uuid.uuid4().hex
