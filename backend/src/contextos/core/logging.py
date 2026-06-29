from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import TextIO

from contextos.core.request_id import get_request_id

LOG_HANDLER_NAME = "contextos"


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, str | dict[str, str]] = {
            "timestamp": datetime.now(UTC)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = getattr(record, "request_id", "-")
        if request_id != "-":
            payload["request_id"] = request_id
        if record.exc_info is not None:
            exception_type = record.exc_info[0]
            payload["exception"] = {
                "type": exception_type.__name__ if exception_type is not None else "UnknownError"
            }
        return json.dumps(payload, ensure_ascii=True)


def build_handler(log_format: str, stream: TextIO | None = None) -> logging.Handler:
    handler = logging.StreamHandler(stream)
    handler.set_name(LOG_HANDLER_NAME)
    handler.addFilter(RequestIdFilter())
    if log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(name)s [%(request_id)s] %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S%z",
            )
        )
    return handler


def configure_logging(log_level: str, log_format: str, stream: TextIO | None = None) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    for handler in list(root_logger.handlers):
        if handler.get_name() == LOG_HANDLER_NAME:
            root_logger.removeHandler(handler)
            handler.close()

    root_logger.addHandler(build_handler(log_format=log_format, stream=stream))
