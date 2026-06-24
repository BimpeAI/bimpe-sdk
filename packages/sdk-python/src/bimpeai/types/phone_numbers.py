from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict
from typing_extensions import NotRequired, TypedDict

PhoneNumberRegion = Literal["us", "uk", "eu", "ng"]


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


class PhoneNumber(_Model):
    id: str
    agent_id: str | None = None
    label: str | None = None
    e164: str


class PhoneNumberDetail(PhoneNumber):
    created_at: str
    updated_at: str
    inbound_enabled: bool


class PhoneNumberRequest(_Model):
    """A provisioning request. Unlike an assigned `PhoneNumber`, it has no `e164`
    until it is fulfilled, so every field other than `id` is optional. Any field
    the server adds is preserved (the model allows extras)."""

    id: str
    status: str | None = None
    business_name: str | None = None
    intended_use: str | None = None
    region: str | None = None
    agent_count: int | None = None
    outbound_minutes: int | None = None
    e164: str | None = None
    agent_id: str | None = None
    label: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ListPhoneNumbersQuery(TypedDict, total=False):
    page: int
    limit: int
    search: str
    sort: str


class CreatePhoneNumberRequestBody(TypedDict):
    business_name: str
    intended_use: str
    region: PhoneNumberRegion
    agent_count: int
    outbound_minutes: int
    submitted_by_agent_id: NotRequired[str]


class UpdatePhoneNumberBody(TypedDict, total=False):
    agent_id: str | None
    label: str
