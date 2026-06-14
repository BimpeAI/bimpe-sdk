from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict
from typing_extensions import NotRequired, TypedDict

ConversationChannel = Literal[
    "whatsapp",
    "messenger",
    "instagram",
    "webchat",
    "test_whatsapp",
    "test_messenger",
    "test_instagram",
]
StreamMessageRole = Literal["user", "assistant", "restaurant_user", "customer"]


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


class Conversation(_Model):
    id: str
    channel_type: str
    channel_id: str | None = None
    is_test_channel: bool
    full_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    channel_username: str | None = None
    is_ai_chat_paused: bool
    last_message_at: str | None = None
    last_message_preview: str | None = None
    created_at: str
    updated_at: str


class Message(_Model):
    id: str
    role: str
    message: str | None = None
    message_type: str | None = None
    created_at: str


class StreamTicket(_Model):
    ticket: str
    expires_in: int


class StreamMessageEvent(_Model):
    id: str
    conversation_id: str
    role: StreamMessageRole
    message: str | None = None
    message_type: str | None = None
    created_at: str


class StreamHeartbeatEvent(_Model):
    ts: int


class MessageAttachment(TypedDict):
    type: str
    url: str


class SendMessageBody(TypedDict):
    message: str
    attachments: NotRequired[list[MessageAttachment]]
