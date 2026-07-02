from __future__ import annotations

import io
import json
import logging
import sys

from contextos.core.logging import JsonFormatter, configure_logging
from contextos.core.request_id import reset_request_id, set_request_id


def test_logging_initialization_is_idempotent() -> None:
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    try:
        configure_logging(log_level="INFO", log_format="json")
        first_count = len(
            [handler for handler in root_logger.handlers if handler.get_name() == "contextos"]
        )
        configure_logging(log_level="INFO", log_format="json")
        second_count = len(
            [handler for handler in root_logger.handlers if handler.get_name() == "contextos"]
        )
        assert first_count == 1
        assert second_count == 1
    finally:
        for handler in list(root_logger.handlers):
            if handler.get_name() == "contextos":
                root_logger.removeHandler(handler)
                handler.close()
        for handler in original_handlers:
            if handler not in root_logger.handlers:
                root_logger.addHandler(handler)


def test_json_log_structure_includes_safe_request_id() -> None:
    stream = io.StringIO()
    root_logger = logging.getLogger()
    try:
        configure_logging(log_level="INFO", log_format="json", stream=stream)
        token = set_request_id("safe-request-id")
        try:
            logging.getLogger("contextos.test").info("hello world")
        finally:
            reset_request_id(token)

        payload = json.loads(stream.getvalue().strip())
        assert payload["level"] == "INFO"
        assert payload["logger"] == "contextos.test"
        assert payload["message"] == "hello world"
        assert payload["request_id"] == "safe-request-id"
        assert "timestamp" in payload
    finally:
        for handler in list(root_logger.handlers):
            if handler.get_name() == "contextos":
                root_logger.removeHandler(handler)
                handler.close()


def test_json_formatter_exception_metadata_stays_safe() -> None:
    formatter = JsonFormatter()
    try:
        raise RuntimeError("postgresql+asyncpg://should-not-appear")
    except RuntimeError:
        record = logging.getLogger("contextos.test").makeRecord(
            name="contextos.test",
            level=logging.ERROR,
            fn=__file__,
            lno=1,
            msg="request failed",
            args=(),
            exc_info=sys.exc_info(),
        )

    payload = json.loads(formatter.format(record))
    assert payload["message"] == "request failed"
    assert payload["exception"] == {"type": "RuntimeError"}
    assert "postgresql+asyncpg://" not in json.dumps(payload)


def test_log_formatter_redacts_tokens_secrets_and_private_content() -> None:
    formatter = JsonFormatter()
    record = logging.getLogger("contextos.test").makeRecord(
        name="contextos.test",
        level=logging.INFO,
        fn=__file__,
        lno=1,
        msg=(
            "Authorization Bearer raw-token-value "
            "api_key=sk_private_secret_value_123456 "
            "document_content=private-pdf-body "
            "memory_content=private-memory"
        ),
        args=(),
        exc_info=None,
    )

    payload = json.loads(formatter.format(record))

    assert "raw-token-value" not in payload["message"]
    assert "sk_private_secret_value" not in payload["message"]
    assert "private-pdf-body" not in payload["message"]
    assert "private-memory" not in payload["message"]
    assert "[redacted]" in payload["message"]
