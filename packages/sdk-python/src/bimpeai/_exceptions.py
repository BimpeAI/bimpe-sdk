from __future__ import annotations

from typing import Any, Literal, cast

import httpx

ErrorCode = Literal[
    "validation_error",
    "bad_request",
    "unauthorized",
    "api_key_missing",
    "api_key_invalid",
    "api_key_expired",
    "insufficient_scope",
    "forbidden",
    "not_found",
    "conflict",
    "rate_limited",
    "too_many_requests",
    "not_implemented",
    "agent_limit_reached",
    "internal_error",
]


class BimpeAIError(Exception):
    """Base class for every error raised by the SDK."""


class UserError(BimpeAIError):
    """The SDK was used or configured incorrectly (e.g. missing api_key)."""


class APIConnectionError(BimpeAIError):
    def __init__(
        self, message: str = "connection error", *, cause: BaseException | None = None
    ) -> None:
        super().__init__(message)
        if cause is not None:
            self.__cause__ = cause


class APITimeoutError(APIConnectionError):
    def __init__(
        self, message: str = "request timed out", *, cause: BaseException | None = None
    ) -> None:
        super().__init__(message, cause=cause)


class APIError(BimpeAIError):
    def __init__(
        self,
        message: str,
        *,
        status: int,
        code: str | None,
        request_id: str | None,
        headers: httpx.Headers,
        body: Any,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.request_id = request_id
        self.headers = headers
        self.body = body


class BadRequestError(APIError):
    pass


class ValidationError(BadRequestError):
    def __init__(self, message: str, *, field_errors: list[dict[str, str]], **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.field_errors = field_errors


class AuthenticationError(APIError):
    pass


class PermissionDeniedError(APIError):
    pass


class NotFoundError(APIError):
    pass


class ConflictError(APIError):
    pass


class RateLimitError(APIError):
    def __init__(
        self,
        message: str,
        *,
        retry_after: int | None,
        limit: int | None,
        remaining: int | None,
        reset_at: int | None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        self.reset_at = reset_at


class InternalServerError(APIError):
    pass


class APINotImplementedError(APIError):
    pass


def map_api_error(status: int, body: Any, headers: httpx.Headers) -> APIError:
    err_body: dict[str, Any] = cast("dict[str, Any]", body) if isinstance(body, dict) else {}
    message = _normalise_message(err_body.get("message")) or f"HTTP {status}"
    code = err_body.get("code")
    request_id = headers.get("x-request-id") or err_body.get("request_id")
    base: dict[str, Any] = {
        "status": status,
        "code": code,
        "request_id": request_id,
        "headers": headers,
        "body": body,
    }

    if status == 400:
        if code == "validation_error":
            return ValidationError(
                message, field_errors=_parse_field_errors(err_body.get("message")), **base
            )
        return BadRequestError(message, **base)
    if status == 401:
        return AuthenticationError(message, **base)
    if status == 403:
        return PermissionDeniedError(message, **base)
    if status == 404:
        return NotFoundError(message, **base)
    if status == 409:
        return ConflictError(message, **base)
    if status == 429:
        return RateLimitError(
            message,
            retry_after=_int_or_none(headers.get("retry-after")),
            limit=_int_or_none(headers.get("x-ratelimit-limit")),
            remaining=_int_or_none(headers.get("x-ratelimit-remaining")),
            reset_at=_int_or_none(headers.get("x-ratelimit-reset")),
            **base,
        )
    if status == 501:
        return APINotImplementedError(message, **base)
    if status >= 500:
        return InternalServerError(message, **base)
    return APIError(message, **base)


def _normalise_message(message: Any) -> str | None:
    if isinstance(message, list):
        parts = cast("list[Any]", message)
        return "; ".join(str(m) for m in parts)
    if isinstance(message, str):
        return message
    return None


def _parse_field_errors(message: Any) -> list[dict[str, str]]:
    if not isinstance(message, list):
        return []
    items = cast("list[Any]", message)
    out: list[dict[str, str]] = []
    for entry in items:
        if not isinstance(entry, str):
            continue
        path, sep, rest = entry.partition(":")
        if sep:
            out.append({"path": path.strip(), "message": rest.strip()})
        else:
            out.append({"path": "", "message": entry})
    return out


def _int_or_none(raw: str | None) -> int | None:
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None
