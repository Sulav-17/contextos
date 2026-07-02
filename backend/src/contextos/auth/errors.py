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
DOCUMENT_NOT_FOUND = ApiErrorSpec(
    code="document_not_found",
    message="Document not found.",
    status_code=status.HTTP_404_NOT_FOUND,
)
DOCUMENT_LIMIT_REACHED = ApiErrorSpec(
    code="document_limit_reached",
    message="Document limit reached.",
    status_code=status.HTTP_409_CONFLICT,
)
DOCUMENT_STORAGE_LIMIT_REACHED = ApiErrorSpec(
    code="document_storage_limit_reached",
    message="Document storage limit reached.",
    status_code=status.HTTP_409_CONFLICT,
)
DOCUMENT_INVALID_FILE = ApiErrorSpec(
    code="document_invalid_file",
    message="Upload a valid PDF file.",
    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
)
DOCUMENT_TOO_LARGE = ApiErrorSpec(
    code="document_too_large",
    message="PDF exceeds the configured size limit.",
    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
)
DOCUMENT_TOO_MANY_PAGES = ApiErrorSpec(
    code="document_too_many_pages",
    message="PDF exceeds the configured page limit.",
    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
)
DOCUMENT_NOT_RETRYABLE = ApiErrorSpec(
    code="document_not_retryable",
    message="Only failed documents can be retried.",
    status_code=status.HTTP_409_CONFLICT,
)
CONVERSATION_NOT_FOUND = ApiErrorSpec(
    code="conversation_not_found",
    message="Conversation not found.",
    status_code=status.HTTP_404_NOT_FOUND,
)
AI_DAILY_LIMIT_REACHED = ApiErrorSpec(
    code="daily_ai_message_limit_reached",
    message="Daily AI message limit reached.",
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
)
AI_MONTHLY_LIMIT_REACHED = ApiErrorSpec(
    code="monthly_ai_message_limit_reached",
    message="Monthly AI message limit reached.",
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
)
AI_PROVIDER_UNAVAILABLE = ApiErrorSpec(
    code="ai_provider_unavailable",
    message="The AI provider is temporarily unavailable.",
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
)
MEMORY_NOT_FOUND = ApiErrorSpec(
    code="memory_not_found",
    message="Memory not found.",
    status_code=status.HTTP_404_NOT_FOUND,
)
MEMORY_DUPLICATE = ApiErrorSpec(
    code="memory_duplicate",
    message="That memory already exists.",
    status_code=status.HTTP_409_CONFLICT,
)
