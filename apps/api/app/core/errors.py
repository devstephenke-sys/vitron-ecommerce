"""Standard API error handling.

All error responses use a consistent envelope::

    {"error": {"code": "...", "message": "...", "request_id": "..."}}

Stack traces and internal details are never exposed to clients; they are
only written to the server logs.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.logging import request_id_var

logger = logging.getLogger("vitron.errors")


def _error_body(code: str, message: str) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id_var.get(),
        }
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Do not echo raw input values back to the client.
        details = [
            {"loc": list(err.get("loc", [])), "msg": err.get("msg", "")} for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed",
                    "details": details,
                    "request_id": request_id_var.get(),
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body("http_error", str(exc.detail)),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        message = "An unexpected error occurred" if get_settings().is_production else str(exc)
        return JSONResponse(
            status_code=500,
            content=_error_body("internal_error", message),
        )
