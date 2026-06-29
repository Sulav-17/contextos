from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from contextos.core.request_id import (
    REQUEST_ID_MAX_LENGTH,
    RequestIdMiddleware,
    get_request_id,
    is_valid_request_id,
    reset_request_id,
    set_request_id,
)


def test_request_id_validation_and_generation_rules() -> None:
    assert is_valid_request_id("safe-request_id.123") is True
    assert is_valid_request_id("bad value") is False
    assert is_valid_request_id("x" * (REQUEST_ID_MAX_LENGTH + 1)) is False


def test_request_context_cleanup() -> None:
    app = FastAPI()
    app.add_middleware(RequestIdMiddleware)

    @app.get("/request-context")
    async def request_context() -> dict[str, str | None]:
        return {"request_id": get_request_id()}

    with TestClient(app) as client:
        first = client.get("/request-context", headers={"X-Request-ID": "first-request"})
        second = client.get("/request-context")

    assert first.json() == {"request_id": "first-request"}
    assert second.json()["request_id"] != "first-request"
    assert get_request_id() is None


def test_request_context_manual_reset() -> None:
    token = set_request_id("manual-request")
    assert get_request_id() == "manual-request"
    reset_request_id(token)
    assert get_request_id() is None
