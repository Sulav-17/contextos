from __future__ import annotations

import asyncio
import hashlib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol

import httpx

from contextos.core.config import Settings


class ProviderError(Exception):
    def __init__(self, code: str = "provider_unavailable") -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True, slots=True)
class ChatRequest:
    system_prompt: str
    user_prompt: str


@dataclass(frozen=True, slots=True)
class ChatResult:
    content: str
    provider: str
    model: str


class EmbeddingProvider(Protocol):
    provider: str
    model: str
    dimension: int

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class ChatProvider(Protocol):
    provider: str
    model: str

    async def generate(self, request: ChatRequest) -> ChatResult: ...


class FakeEmbeddingProvider:
    provider = "fake"

    def __init__(self, model: str, dimension: int) -> None:
        self.model = model
        self.dimension = dimension

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [_fake_embedding(text, self.dimension) for text in texts]


class FakeChatProvider:
    provider = "fake"

    def __init__(self, model: str) -> None:
        self.model = model

    async def generate(self, request: ChatRequest) -> ChatResult:
        if request.user_prompt.startswith("General question:\n"):
            question = request.user_prompt.split("General question:\n", 1)[-1].strip()
            answer = f"General answer: {question[:240]}"
            return ChatResult(content=answer, provider=self.provider, model=self.model)
        context_marker = "Document context"
        memory_marker = "\n\nApproved saved memory"
        question_marker = "\n\nQuestion:"
        if request.user_prompt.startswith(context_marker):
            after_context_heading = request.user_prompt.split(":\n", 1)[-1]
            context = after_context_heading.split(memory_marker, 1)[0]
            after_memory_heading = request.user_prompt.split(memory_marker, 1)[-1]
            memory = after_memory_heading.split(":\n", 1)[-1].split(question_marker, 1)[0]
        else:
            context = request.user_prompt.split("Context:\n", 1)[-1].split(question_marker, 1)[0]
            memory = ""
        first_line = next((line for line in context.splitlines() if line.strip()), "")
        first_memory = next((line for line in memory.splitlines() if line.strip()), "")
        answer = (
            "I could not find enough evidence in your documents to answer that."
            if not first_line and not first_memory
            else f"Remembered information: {first_memory[:240]}"
            if not first_line
            else f"Based on your documents, {first_line[:240]}"
        )
        return ChatResult(content=answer, provider=self.provider, model=self.model)


class GeminiEmbeddingProvider:
    provider = "gemini"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.embedding_model
        self.dimension = settings.embedding_dimension
        self._api_key = _api_key(settings)
        self._timeout = settings.ai_provider_timeout_seconds
        self._retries = settings.ai_provider_max_retries

    async def embed(self, texts: list[str]) -> list[list[float]]:
        async def call() -> list[list[float]]:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                vectors: list[list[float]] = []
                for text in texts:
                    response = await client.post(
                        _gemini_url(self.model, "embedContent"),
                        headers={"x-goog-api-key": self._api_key},
                        json={
                            "model": f"models/{self.model}",
                            "content": {"parts": [{"text": text}]},
                            "outputDimensionality": self.dimension,
                        },
                    )
                    _raise_for_provider(response)
                    payload = response.json()
                    values = payload.get("embedding", {}).get("values", [])
                    if not isinstance(values, list) or len(values) != self.dimension:
                        raise ProviderError()
                    vectors.append([float(value) for value in values])
                return vectors

        return await _retry(call, self._retries)


class GeminiChatProvider:
    provider = "gemini"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.llm_model
        self._api_key = _api_key(settings)
        self._timeout = settings.ai_provider_timeout_seconds
        self._retries = settings.ai_provider_max_retries

    async def generate(self, request: ChatRequest) -> ChatResult:
        async def call() -> ChatResult:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    _gemini_url(self.model, "generateContent"),
                    headers={"x-goog-api-key": self._api_key},
                    json={
                        "systemInstruction": {
                            "parts": [{"text": request.system_prompt}]
                        },
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": request.user_prompt}],
                            }
                        ],
                    },
                )
                _raise_for_provider(response)
                payload = response.json()
                candidates = payload.get("candidates", [])
                parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
                text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
                if not text.strip():
                    raise ProviderError()
                return ChatResult(
                    content=text.strip()[:12000],
                    provider=self.provider,
                    model=self.model,
                )

        return await _retry(call, self._retries)


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "gemini":
        return GeminiEmbeddingProvider(settings)
    return FakeEmbeddingProvider(settings.embedding_model, settings.embedding_dimension)


def build_chat_provider(settings: Settings) -> ChatProvider:
    if settings.llm_provider == "gemini":
        return GeminiChatProvider(settings)
    return FakeChatProvider(settings.llm_model)


def _fake_embedding(text: str, dimension: int) -> list[float]:
    words = text.casefold().split()
    vector = [0.0] * dimension
    for word in words or [text]:
        digest = hashlib.sha256(word.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimension
        vector[index] += 1.0
    magnitude = sum(value * value for value in vector) ** 0.5 or 1.0
    return [round(value / magnitude, 8) for value in vector]


def _api_key(settings: Settings) -> str:
    if settings.ai_provider_api_key is None:
        raise ProviderError("provider_not_configured")
    return settings.ai_provider_api_key.get_secret_value()


def _gemini_url(model: str, method: str) -> str:
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:{method}"


def _raise_for_provider(response: httpx.Response) -> None:
    if response.status_code in {408, 409, 425, 429, 500, 502, 503, 504}:
        raise ProviderError()
    if response.status_code >= 400:
        raise ProviderError("provider_rejected_request")


async def _retry[T](operation: Callable[[], Awaitable[T]], retries: int) -> T:
    for attempt in range(retries + 1):
        try:
            return await operation()
        except (httpx.TimeoutException, httpx.TransportError, ProviderError) as exc:
            if isinstance(exc, ProviderError) and exc.code not in {
                "provider_unavailable",
                "provider_not_configured",
            }:
                raise
            if attempt >= retries:
                raise ProviderError(
                    exc.code if isinstance(exc, ProviderError) else "provider_unavailable"
                ) from exc
            await asyncio.sleep(0.2 * (attempt + 1))
    raise ProviderError()
