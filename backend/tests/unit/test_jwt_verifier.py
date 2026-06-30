from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any, ClassVar
from uuid import uuid4

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

from contextos.auth.jwt import AuthenticationError, SupabaseJwtVerifier
from contextos.core.config import Settings


class MockAsyncClient:
    payloads: ClassVar[list[dict[str, Any]]] = []
    calls: ClassVar[int] = 0

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout

    async def __aenter__(self) -> MockAsyncClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def get(self, url: str) -> httpx.Response:
        MockAsyncClient.calls += 1
        request = httpx.Request("GET", url)
        return httpx.Response(200, json=MockAsyncClient.payloads.pop(0), request=request)


@pytest.fixture
def keypair() -> tuple[Any, dict[str, Any]]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(RSAAlgorithm.to_jwk(private_key.public_key()))
    jwk["kid"] = "test-key"
    jwk["alg"] = "RS256"
    return private_key, jwk


@pytest.fixture
def jwt_settings(make_settings: Callable[..., Settings]) -> Settings:
    return make_settings(
        supabase_url="https://project.supabase.co",
        supabase_jwt_issuer="https://project.supabase.co/auth/v1",
        supabase_jwks_url="https://project.supabase.co/auth/v1/.well-known/jwks.json",
        supabase_jwt_audience="authenticated",
    )


def make_token(private_key: Any, settings: Settings, **overrides: object) -> str:
    now = int(time.time())
    claims: dict[str, object] = {
        "sub": str(uuid4()),
        "aud": settings.supabase_jwt_audience,
        "iss": settings.supabase_jwt_issuer,
        "exp": now + 300,
        "iat": now,
        "role": "authenticated",
        "session_id": str(uuid4()),
    }
    claims.update(overrides)
    return jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": "test-key"})


@pytest.mark.asyncio
async def test_verifier_accepts_valid_token(
    monkeypatch: pytest.MonkeyPatch,
    keypair: tuple[Any, dict[str, Any]],
    jwt_settings: Settings,
) -> None:
    private_key, jwk = keypair
    MockAsyncClient.payloads = [{"keys": [jwk]}]
    MockAsyncClient.calls = 0
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    principal = await SupabaseJwtVerifier(jwt_settings).verify_token(
        make_token(private_key, jwt_settings)
    )

    assert principal.subject is not None
    assert MockAsyncClient.calls == 1


@pytest.mark.parametrize(
    "claim_overrides",
    [
        {"iss": "https://wrong.example/auth/v1"},
        {"aud": "wrong"},
        {"role": "anon"},
        {"sub": "not-a-uuid"},
        {"exp": 1},
    ],
)
@pytest.mark.asyncio
async def test_verifier_rejects_invalid_claims(
    monkeypatch: pytest.MonkeyPatch,
    keypair: tuple[Any, dict[str, Any]],
    jwt_settings: Settings,
    claim_overrides: dict[str, object],
) -> None:
    private_key, jwk = keypair
    MockAsyncClient.payloads = [{"keys": [jwk]}]
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    with pytest.raises(AuthenticationError):
        await SupabaseJwtVerifier(jwt_settings).verify_token(
            make_token(private_key, jwt_settings, **claim_overrides)
        )


@pytest.mark.asyncio
async def test_verifier_refreshes_unknown_kid_once(
    monkeypatch: pytest.MonkeyPatch,
    keypair: tuple[Any, dict[str, Any]],
    jwt_settings: Settings,
) -> None:
    private_key, jwk = keypair
    MockAsyncClient.payloads = [{"keys": []}, {"keys": [jwk]}]
    MockAsyncClient.calls = 0
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    await SupabaseJwtVerifier(jwt_settings).verify_token(make_token(private_key, jwt_settings))

    assert MockAsyncClient.calls == 2


@pytest.mark.asyncio
async def test_verifier_uses_jwks_cache(
    monkeypatch: pytest.MonkeyPatch,
    keypair: tuple[Any, dict[str, Any]],
    jwt_settings: Settings,
) -> None:
    private_key, jwk = keypair
    MockAsyncClient.payloads = [{"keys": [jwk]}]
    MockAsyncClient.calls = 0
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)
    verifier = SupabaseJwtVerifier(jwt_settings)

    await verifier.verify_token(make_token(private_key, jwt_settings))
    await verifier.verify_token(make_token(private_key, jwt_settings))

    assert MockAsyncClient.calls == 1
