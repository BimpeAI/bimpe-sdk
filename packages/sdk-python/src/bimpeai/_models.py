from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar, cast

import httpx
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginationMeta(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)

    total_count: int
    page_count: int
    current_page: int
    limit: int
    has_next_page: bool
    has_previous_page: bool


@dataclass(frozen=True, slots=True)
class ApiResponse(Generic[T]):
    data: T
    meta: PaginationMeta | None
    request_id: str | None
    status: int
    headers: httpx.Headers


@dataclass(frozen=True, slots=True)
class Unwrapped:
    data: Any
    meta: PaginationMeta | None


def unwrap_envelope(body: Any) -> Unwrapped:
    if not isinstance(body, dict):
        raise TypeError("Response is not a BimpeAI envelope (missing `message` field)")
    envelope = cast("dict[str, Any]", body)
    if not isinstance(envelope.get("message"), str):
        raise TypeError("Response is not a BimpeAI envelope (missing `message` field)")
    meta_raw = envelope.get("meta")
    meta = PaginationMeta.model_validate(meta_raw) if isinstance(meta_raw, dict) else None
    return Unwrapped(data=envelope.get("data"), meta=meta)
