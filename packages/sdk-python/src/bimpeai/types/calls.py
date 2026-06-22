from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict
from typing_extensions import TypedDict

CallStatus = Literal[
    "queued",
    "ringing",
    "answered",
    "ended",
    "busy",
    "failed",
    "cancelled",
]
MakeCallStatus = Literal["initiated", "busy", "failed"]


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


class Call(_Model):
    id: str
    source: str | None = None
    destination: str
    status: CallStatus
    direction: str
    created_on: str
    duration_seconds: int | None = None
    is_test_call: bool
    error_reason: str | None = None
    end_reason: str | None = None
    ringing_at: str | None = None
    ended_at: str | None = None


class CallMessageAttachment(_Model):
    type: str
    url: str


class CallMessage(_Model):
    id: str
    role: str
    message: str | None = None
    message_type: str | None = None
    created_at: str
    attachments: list[CallMessageAttachment] | None = None


class CallDetail(Call):
    started_at: str | None = None
    answered_at: str | None = None
    conversation_logs: list[CallMessage] = []


class MakeCallResult(_Model):
    status: MakeCallStatus
    call_id: str | None = None
    detail: str | None = None


class ListCallsQuery(TypedDict, total=False):
    page: int
    limit: int
    search: str
    sort: str
    is_test_call: bool
    status: CallStatus


class MakeCallBody(TypedDict):
    destination: str
    is_test_call: bool
