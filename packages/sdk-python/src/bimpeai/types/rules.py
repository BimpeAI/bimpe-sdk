from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from typing_extensions import NotRequired, TypedDict


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


class Rule(_Model):
    id: str
    name: str
    trigger: str
    condition: str | None = None
    response: str
    action: str | None = None
    enabled: bool


class RuleInput(TypedDict):
    id: str
    name: str
    trigger: str
    response: str
    enabled: bool
    condition: NotRequired[str | None]
    action: NotRequired[str | None]
