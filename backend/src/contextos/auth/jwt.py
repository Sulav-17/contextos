from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

import httpx
import jwt
from jwt import PyJWKClientError

from contextos.auth.errors import AUTHENTICATION_REQUIRED, INVALID_AUTHENTICATION
from contextos.auth.principal import Principal
from contextos.core.config import Settings


class AuthenticationError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class AuthProvider(Protocol):
    async def verify_authorization_header(self, authorization: str | None) -> Principal: ...


@dataclass(frozen=True)
class CachedJwks:
    keys: dict[str, Any]
    expires_at: float


class SupabaseJwtVerifier:
    def __init__(self, settings: Settings) -> None:
        self._issuer = settings.supabase_jwt_issuer
        self._audience = settings.supabase_jwt_audience
        self._jwks_url = settings.supabase_jwks_url
        self._algorithms = settings.supabase_allowed_jwt_algorithms
        self._ttl_seconds = settings.supabase_jwks_cache_ttl_seconds
        self._leeway_seconds = settings.supabase_jwt_clock_skew_seconds
        self._cache: CachedJwks | None = None

    async def verify_authorization_header(self, authorization: str | None) -> Principal:
        token = self._extract_bearer(authorization)
        return await self.verify_token(token)

    async def verify_token(self, token: str) -> Principal:
        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError as exc:
            raise AuthenticationError(INVALID_AUTHENTICATION.code) from exc

        algorithm = header.get("alg")
        key_id = header.get("kid")
        if algorithm not in self._algorithms or not isinstance(key_id, str):
            raise AuthenticationError(INVALID_AUTHENTICATION.code)

        key = await self._get_signing_key(key_id, refresh=False)
        if key is None:
            key = await self._get_signing_key(key_id, refresh=True)
        if key is None:
            raise AuthenticationError(INVALID_AUTHENTICATION.code)

        try:
            claims = jwt.decode(
                token,
                key=key,
                algorithms=list(self._algorithms),
                audience=self._audience,
                issuer=self._issuer,
                leeway=self._leeway_seconds,
                options={"require": ["exp", "sub"]},
            )
        except jwt.PyJWTError as exc:
            raise AuthenticationError(INVALID_AUTHENTICATION.code) from exc

        if claims.get("role") != "authenticated":
            raise AuthenticationError(INVALID_AUTHENTICATION.code)

        subject = self._claim_uuid(claims.get("sub"))
        session_id = self._optional_uuid(claims.get("session_id"))
        email = claims.get("email") if isinstance(claims.get("email"), str) else None
        return Principal(subject=subject, email=email, session_id=session_id)

    def _extract_bearer(self, authorization: str | None) -> str:
        if not authorization:
            raise AuthenticationError(AUTHENTICATION_REQUIRED.code)
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token or " " in token:
            raise AuthenticationError(INVALID_AUTHENTICATION.code)
        return token

    async def _get_signing_key(self, key_id: str, refresh: bool) -> Any | None:
        jwks = await self._get_jwks(refresh=refresh)
        key_data = jwks.get(key_id)
        if key_data is None:
            return None
        try:
            return jwt.PyJWK.from_dict(key_data).key
        except PyJWKClientError as exc:
            raise AuthenticationError(INVALID_AUTHENTICATION.code) from exc

    async def _get_jwks(self, refresh: bool) -> dict[str, Any]:
        now = time.monotonic()
        if not refresh and self._cache is not None and self._cache.expires_at > now:
            return self._cache.keys

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(self._jwks_url)
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AuthenticationError(INVALID_AUTHENTICATION.code) from exc

        keys = payload.get("keys")
        if not isinstance(keys, list):
            raise AuthenticationError(INVALID_AUTHENTICATION.code)
        parsed = {
            key["kid"]: key
            for key in keys
            if isinstance(key, dict) and isinstance(key.get("kid"), str)
        }
        self._cache = CachedJwks(keys=parsed, expires_at=now + self._ttl_seconds)
        return parsed

    def _claim_uuid(self, value: object) -> UUID:
        if not isinstance(value, str):
            raise AuthenticationError(INVALID_AUTHENTICATION.code)
        try:
            return UUID(value)
        except ValueError as exc:
            raise AuthenticationError(INVALID_AUTHENTICATION.code) from exc

    def _optional_uuid(self, value: object) -> UUID | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise AuthenticationError(INVALID_AUTHENTICATION.code)
        return self._claim_uuid(value)
