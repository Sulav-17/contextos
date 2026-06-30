from __future__ import annotations

from dataclasses import dataclass

from fastapi import status


@dataclass(frozen=True)
class ApiErrorSpec:
    code: str
    message: str
    status_code: int


AUTHENTICATION_REQUIRED = ApiErrorSpec(
    code="authentication_required",
    message="Authentication is required.",
    status_code=status.HTTP_401_UNAUTHORIZED,
)
INVALID_AUTHENTICATION = ApiErrorSpec(
    code="invalid_authentication",
    message="Authentication could not be verified.",
    status_code=status.HTTP_401_UNAUTHORIZED,
)
USER_NOT_PROVISIONED = ApiErrorSpec(
    code="user_not_provisioned",
    message="This account is not provisioned for ContextOS.",
    status_code=status.HTTP_403_FORBIDDEN,
)
ACCOUNT_DISABLED = ApiErrorSpec(
    code="account_disabled",
    message="This account is disabled.",
    status_code=status.HTTP_403_FORBIDDEN,
)
ADMINISTRATOR_REQUIRED = ApiErrorSpec(
    code="administrator_required",
    message="Administrator access is required.",
    status_code=status.HTTP_403_FORBIDDEN,
)
INVITATION_DUPLICATE = ApiErrorSpec(
    code="invitation_duplicate",
    message="An active invitation already exists for that email.",
    status_code=status.HTTP_409_CONFLICT,
)
BETA_CAPACITY_REACHED = ApiErrorSpec(
    code="beta_capacity_reached",
    message="The beta user capacity has been reached.",
    status_code=status.HTTP_409_CONFLICT,
)
PROVIDER_UNAVAILABLE = ApiErrorSpec(
    code="provider_unavailable",
    message="Invitation delivery is temporarily unavailable.",
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
)
VALIDATION_FAILED = ApiErrorSpec(
    code="validation_failed",
    message="The request body is invalid.",
    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
)
