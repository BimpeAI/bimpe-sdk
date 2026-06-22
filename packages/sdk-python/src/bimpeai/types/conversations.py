from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict
from typing_extensions import NotRequired, TypedDict

ConversationChannel = Literal[
    "whatsapp",
    "webchat",
    "telephony",
    "test_whatsapp",
    "test_webchat",
    "test_telephony",
]
MessageRole = Literal["user", "assistant"]
StreamMessageRole = Literal["user", "assistant", "restaurant_user", "customer"]


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


class Conversation(_Model):
    id: str
    channel_type: str
    channel_id: str | None = None
    channel_user_id: str | None = None
    channel_user_username: str | None = None
    is_test_channel: bool
    is_ai_chat_paused: bool
    needs_attention: bool
    last_message_at: str | None = None
    last_seen: str | None = None
    last_message_preview: str | None = None
    created_at: str
    updated_at: str


class ConversationDetail(Conversation):
    full_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    profile_picture: str | None = None


class MessageAttachment(_Model):
    type: str
    url: str


class Message(_Model):
    id: str
    role: str
    message: str | None = None
    message_type: str | None = None
    created_at: str
    attachments: list[MessageAttachment] | None = None


class ConversationAiStatus(_Model):
    is_ai_chat_paused: bool | None = None


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


class ListConversationsQuery(TypedDict, total=False):
    page: int
    limit: int
    search: str
    sort: str
    channel: ConversationChannel
    is_test_channel: bool
    is_ai_chat_paused: bool
    needs_attention: bool


class CreateConversationMessageBody(TypedDict):
    message: str
    role: NotRequired[MessageRole]
    conversation_id: NotRequired[str]
    channel_type: NotRequired[Literal["whatsapp", "webchat", "telephony"]]
    channel_user_id: NotRequired[str]
    channel_username: NotRequired[str]
    is_test_channel: NotRequired[bool]


class SetAiStatusBody(TypedDict):
    is_ai_chat_paused: bool


class SendMessageBody(TypedDict):
    message: str
    role: NotRequired[MessageRole]


class ListMessagesQuery(TypedDict, total=False):
    page: int
    limit: int
    search: str
    sort: str
