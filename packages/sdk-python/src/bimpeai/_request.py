from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Method = Literal["GET", "POST", "PATCH", "PUT", "DELETE"]


@dataclass(frozen=True, slots=True)
class RequestOptions:
    idempotency_key: str | None = None
    timeout: float | None = None
    max_retries: int | None = None
    headers: dict[str, str] | None = None


@dataclass(frozen=True, slots=True)
class RequestSpec:
    method: Method
    path: str
    query: dict[str, Any] | None = None
    body: Any = None
    options: RequestOptions = field(default_factory=RequestOptions)


@dataclass(frozen=True, slots=True)
class StreamSpec:
    path: str
    query: dict[str, Any] | None = None
    timeout: float | None = None
    headers: dict[str, str] | None = None
