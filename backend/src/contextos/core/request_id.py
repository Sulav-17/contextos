from __future__ import annotations

import re
from contextvars import ContextVar, Token
from typing import Final
from uuid import uuid4

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER: Final[str] = "X-Request-ID"
REQUEST_ID_MAX_LENGTH: Final[int] = 64
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

_request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


def is_valid_request_id(candidate: str | None) -> bool:
    return bool(
        candidate
        and len(candidate) <= REQUEST_ID_MAX_LENGTH
        and REQUEST_ID_PATTERN.fullmatch(candidate) is not None
    )


def generate_request_id() -> str:
    return str(uuid4())


def get_request_id() -> str | None:
    return _request_id_context.get()


def set_request_id(value: str) -> Token[str | None]:
    return _request_id_context.set(value)


def reset_request_id(token: Token[str | None]) -> None:
    _request_id_context.reset(token)


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = MutableHeaders(scope=scope)
        incoming_request_id = headers.get(REQUEST_ID_HEADER)
        request_id = (
            incoming_request_id
            if incoming_request_id is not None and is_valid_request_id(incoming_request_id)
            else generate_request_id()
        )
        token = set_request_id(request_id)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                response_headers[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            reset_request_id(token)
