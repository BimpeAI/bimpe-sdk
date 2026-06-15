from __future__ import annotations

from ._request_id import generate_request_id


def resolve_idempotency_key(supplied: str | None, max_retries: int) -> str | None:
    if supplied:
        return supplied
    if max_retries > 0:
        return generate_request_id()
    return None
