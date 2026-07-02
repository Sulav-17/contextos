from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from typing import TextIO

from contextos.core.request_id import get_request_id

LOG_HANDLER_NAME = "contextos"
REDACTION_PATTERNS = (
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]+", re.I),
    re.compile(r"\b(?:sk|pk)_[A-Za-z0-9_]{16,}\b"),
    re.compile(r"\b[A-Za-z0-9_=-]{24,}\.[A-Za-z0-9_=-]{12,}\.[A-Za-z0-9_=-]{12,}\b"),
    re.compile(r"postgresql(?:\+\w+)?://[^ \t\r\n]+", re.I),
    re.compile(r"redis://[^ \t\r\n]+", re.I),
    re.compile(r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|password)=([^&\s]+)"),
    re.compile(r"(?i)(document|memory|prompt)_content=([^&\s]+)"),
)


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
            "message": redact_log_text(record.getMessage()),
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


class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        original_msg = record.msg
        original_args = record.args
        record.msg = redact_log_text(record.getMessage())
        record.args = ()
        try:
            return super().format(record)
        finally:
            record.msg = original_msg
            record.args = original_args


def redact_log_text(value: str) -> str:
    redacted = value
    for pattern in REDACTION_PATTERNS:
        redacted = pattern.sub(lambda match: _redaction_replacement(match), redacted)
    return redacted


def _redaction_replacement(match: re.Match[str]) -> str:
    if match.lastindex and match.lastindex >= 1:
        return f"{match.group(1)}=[redacted]"
    return "[redacted]"


def build_handler(log_format: str, stream: TextIO | None = None) -> logging.Handler:
    handler = logging.StreamHandler(stream)
    handler.set_name(LOG_HANDLER_NAME)
    handler.addFilter(RequestIdFilter())
    if log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            RedactingFormatter(
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
