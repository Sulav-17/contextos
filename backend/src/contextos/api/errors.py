from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from contextos.auth.errors import ApiErrorSpec
from contextos.core.request_id import get_request_id


class ContextOSError(HTTPException):
    def __init__(self, spec: ApiErrorSpec) -> None:
        super().__init__(status_code=spec.status_code, detail=spec)


def error_payload(spec: ApiErrorSpec) -> dict[str, dict[str, str]]:
    return {
        "error": {
            "code": spec.code,
            "message": spec.message,
            "request_id": get_request_id() or "",
        }
    }


async def contextos_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, ContextOSError):
        raise exc
    spec = exc.detail
    if not isinstance(spec, ApiErrorSpec):
        raise exc
    return JSONResponse(status_code=spec.status_code, content=error_payload(spec))
