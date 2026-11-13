"""Structured logging configuration with request correlation IDs."""

import logging
import sys
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Attach the current request ID to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def setup_logging(level: str = "INFO") -> None:
    """Configure JSON-ish structured logging to stdout.

    Output is a single line per record with key=value fields so log
    aggregation platforms can parse it without a heavy dependency.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s level=%(levelname)s logger=%(name)s request_id=%(request_id)s %(message)s"
        )
    )
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())


def new_request_id() -> str:
    return uuid.uuid4().hex


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
