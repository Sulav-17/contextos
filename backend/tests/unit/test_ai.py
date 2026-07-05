from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from contextos.core.config import Settings
from contextos.domain.ai import (
    ChatRequest,
    ProviderError,
    build_chat_provider,
    build_embedding_provider,
)


class FakeResponse:
    def __init__(self, payload: dict[str, object], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict[str, object]:
        return self._payload


class RecordingAsyncClient:
    last_request: dict[str, Any] | None = None
    response: FakeResponse = FakeResponse({})

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout

    async def __aenter__(self) -> RecordingAsyncClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        return None

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> FakeResponse:
        self.__class__.last_request = {"url": url, "headers": headers or {}, "json": json or {}}
        return self.__class__.response


@pytest.mark.asyncio
async def test_fake_embeddings_are_deterministic(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(embedding_provider="fake", embedding_dimension=8)
    provider = build_embedding_provider(settings)

    first = await provider.embed(["alpha beta"])
    second = await provider.embed(["alpha beta"])

    assert first == second
    assert len(first[0]) == 8


def test_gemini_embedding_requires_server_side_key(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(embedding_provider="gemini", ai_provider_api_key=None)

    with pytest.raises(ProviderError) as exc:
        build_embedding_provider(settings)

    assert exc.value.code == "provider_not_configured"


@pytest.mark.asyncio
async def test_gemini_embedding_uses_header_and_configured_dimension(
    make_settings: Callable[..., Settings],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = make_settings(
        embedding_provider="gemini",
        ai_provider_api_key="super-secret",
        embedding_model="text-embedding-004",
        embedding_dimension=768,
    )
    RecordingAsyncClient.response = FakeResponse({"embedding": {"values": [0.0] * 768}})
    monkeypatch.setattr("contextos.domain.ai.httpx.AsyncClient", RecordingAsyncClient)

    provider = build_embedding_provider(settings)
    await provider.embed(["hello world"])

    assert RecordingAsyncClient.last_request is not None
    assert RecordingAsyncClient.last_request["url"] == (
        "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
    )
    assert "super-secret" not in str(RecordingAsyncClient.last_request["url"])
    assert RecordingAsyncClient.last_request["headers"] == {"x-goog-api-key": "super-secret"}
    assert RecordingAsyncClient.last_request["json"]["outputDimensionality"] == 768


@pytest.mark.asyncio
async def test_gemini_chat_uses_header_without_key_in_url(
    make_settings: Callable[..., Settings],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = make_settings(llm_provider="gemini", ai_provider_api_key="chat-secret")
    RecordingAsyncClient.response = FakeResponse(
        {"candidates": [{"content": {"parts": [{"text": "Grounded answer."}]}}]}
    )
    monkeypatch.setattr("contextos.domain.ai.httpx.AsyncClient", RecordingAsyncClient)

    provider = build_chat_provider(settings)
    await provider.generate(ChatRequest(system_prompt="sys", user_prompt="user"))

    assert RecordingAsyncClient.last_request is not None
    assert RecordingAsyncClient.last_request["url"] == (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    )
    assert "chat-secret" not in str(RecordingAsyncClient.last_request["url"])
    assert RecordingAsyncClient.last_request["headers"] == {"x-goog-api-key": "chat-secret"}


@pytest.mark.asyncio
async def test_gemini_embedding_rejects_wrong_dimension(
    make_settings: Callable[..., Settings],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = make_settings(
        embedding_provider="gemini",
        ai_provider_api_key="super-secret",
        embedding_dimension=768,
    )
    RecordingAsyncClient.response = FakeResponse({"embedding": {"values": [0.0] * 767}})
    monkeypatch.setattr("contextos.domain.ai.httpx.AsyncClient", RecordingAsyncClient)

    provider = build_embedding_provider(settings)

    with pytest.raises(ProviderError):
        await provider.embed(["hello world"])
