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
CreateOrSendChannelType = Literal["whatsapp", "webchat", "telephony"]
MessageRole = Literal["user", "assistant"]
StreamMessageRole = Literal["user", "assistant", "restaurant_user", "customer"]


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


class ConversationListItem(_Model):
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


class Conversation(ConversationListItem):
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
    attachments: list[MessageAttachment] = []


class CreateOrSendMessageResponse(Message):
    conversation_id: str


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


class SendMessageBody(TypedDict):
    message: str
    role: NotRequired[MessageRole]


class SendToConversationBody(TypedDict):
    message: str
    role: NotRequired[MessageRole]


class CreateOrSendExistingBody(SendToConversationBody):
    conversation_id: str


class CreateOrSendByChannelBody(SendToConversationBody):
    channel_type: CreateOrSendChannelType
    channel_user_id: str
    channel_username: NotRequired[str]
    is_test_channel: NotRequired[bool]


CreateOrSendMessageBody = CreateOrSendExistingBody | CreateOrSendByChannelBody


class UpdateAiStatusBody(TypedDict):
    is_ai_chat_paused: bool


class UpdateAiStatusResponse(_Model):
    is_ai_chat_paused: bool
