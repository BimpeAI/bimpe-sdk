from __future__ import annotations

import random

from ._exceptions import (
    APIConnectionError,
    APIError,
    APINotImplementedError,
    BimpeAIError,
    ConflictError,
)

DEFAULT_BASE_S = 0.5
DEFAULT_MAX_BACKOFF_S = 8.0

_RETRYABLE_STATUSES = {408, 429}


def should_retry(error: object, attempt: int, max_retries: int) -> bool:
    if attempt >= max_retries:
        return False
    if not isinstance(error, BimpeAIError):
        return False
    if isinstance(error, APIConnectionError):
        return True
    if isinstance(error, (APINotImplementedError, ConflictError)):
        return False
    if isinstance(error, APIError):
        if error.status in _RETRYABLE_STATUSES:
            return True
        if error.status >= 500 and error.status != 501:
            return True
    return False


def compute_backoff(
    attempt: int,
    base_s: float = DEFAULT_BASE_S,
    max_s: float = DEFAULT_MAX_BACKOFF_S,
    *,
    retry_after_s: float | None = None,
) -> float:
    if retry_after_s is not None and retry_after_s >= 0:
        return min(retry_after_s, max_s)
    exponential = min(max_s, base_s * (2**attempt))
    return exponential * (0.5 + random.random() * 0.5)
