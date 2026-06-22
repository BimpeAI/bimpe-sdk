from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any

import httpx

from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec, StreamSpec
from bimpeai.pagination import Page
from bimpeai.resources.conversations import AsyncConversations, Conversations
from bimpeai.types.conversations import ConversationAiStatus, ConversationDetail, Message

CONVERSATION: dict[str, Any] = {
    "id": "cv_1",
    "channel_type": "whatsapp",
    "channel_id": None,
    "is_test_channel": False,
    "is_ai_chat_paused": False,
    "needs_attention": False,
    "last_message_at": None,
    "last_message_preview": None,
    "created_at": "t",
    "updated_at": "t",
}

MESSAGE: dict[str, Any] = {
    "id": "m_1",
    "role": "user",
    "message": "Hi there",
    "message_type": "text",
    "created_at": "now",
}


def response(data: Any) -> ApiResponse[Any]:
    return ApiResponse(data=data, meta=None, request_id="r", status=200, headers=httpx.Headers())


class FakeSync:
    def __init__(self, data: Any) -> None:
        self._data = data
        self.specs: list[RequestSpec] = []

    def request(self, spec: RequestSpec) -> ApiResponse[Any]:
        self.specs.append(spec)
        return response(self._data)

    @contextmanager
    def stream(self, spec: StreamSpec) -> Generator[httpx.Response, None, None]:
        yield httpx.Response(200, content=b"", request=httpx.Request("GET", "https://x"))


class FakeAsync:
    def __init__(self, data: Any) -> None:
        self._data = data
        self.specs: list[RequestSpec] = []

    async def request(self, spec: RequestSpec) -> ApiResponse[Any]:
        self.specs.append(spec)
        return response(self._data)

    @asynccontextmanager
    async def stream(self, spec: StreamSpec) -> AsyncGenerator[httpx.Response, None]:
        yield httpx.Response(200, content=b"", request=httpx.Request("GET", "https://x"))


def test_list_forwards_every_filter() -> None:
    client = FakeSync([CONVERSATION])
    page = Conversations(client).list(
        "a_1",
        channel="whatsapp",
        sort="-created_at",
        is_test_channel=False,
        is_ai_chat_paused=True,
        needs_attention=True,
    )
    assert isinstance(page, Page)
    spec = client.specs[-1]
    assert spec.method == "GET"
    assert spec.path == "/agents/a_1/conversations"
    assert spec.query == {
        "page": 1,
        "limit": None,
        "search": None,
        "sort": "-created_at",
        "channel": "whatsapp",
        "is_test_channel": False,
        "is_ai_chat_paused": True,
        "needs_attention": True,
    }


def test_retrieve_returns_detail_shape() -> None:
    detail: dict[str, Any] = {
        **CONVERSATION,
        "full_name": "Ada Lovelace",
        "email": "ada@example.com",
        "phone_number": "+15551234567",
        "profile_picture": None,
    }
    client = FakeSync(detail)
    conversations = Conversations(client)
    out = conversations.retrieve("a_1", "cv_1")
    assert isinstance(out, ConversationDetail)
    assert out.id == "cv_1"
    assert out.full_name == "Ada Lovelace"
    assert out.email == "ada@example.com"
    assert client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1/conversations/cv_1")
    assert conversations.messages is not None


def test_send_posts_collection_level_messages_path() -> None:
    client = FakeSync(MESSAGE)
    body: dict[str, Any] = {
        "message": "Hi there",
        "channel_type": "whatsapp",
        "channel_user_id": "+15551234567",
        "channel_username": "ada",
    }
    msg = Conversations(client).send("a_1", idempotency_key="op-1", **body)
    assert isinstance(msg, Message)
    assert msg.id == "m_1"
    spec = client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents/a_1/conversations/messages"
    assert spec.body == body
    assert spec.options.idempotency_key == "op-1"


def test_set_ai_status_patches_ai_status_path() -> None:
    client = FakeSync({"is_ai_chat_paused": True})
    status = Conversations(client).set_ai_status("a_1", "cv_1", is_ai_chat_paused=True)
    assert isinstance(status, ConversationAiStatus)
    assert status.is_ai_chat_paused is True
    spec = client.specs[-1]
    assert spec.method == "PATCH"
    assert spec.path == "/agents/a_1/conversations/cv_1/ai-status"
    assert spec.body == {"is_ai_chat_paused": True}


def test_list_accepts_telephony_and_test_webchat_channels() -> None:
    client = FakeSync([{**CONVERSATION, "channel_type": "telephony"}])
    Conversations(client).list("a_1", channel="telephony")
    telephony_query = client.specs[-1].query
    assert telephony_query is not None
    assert telephony_query["channel"] == "telephony"
    Conversations(client).list("a_1", channel="test_webchat")
    webchat_query = client.specs[-1].query
    assert webchat_query is not None
    assert webchat_query["channel"] == "test_webchat"


async def test_async_list_and_send() -> None:
    list_client = FakeAsync([CONVERSATION])
    page = await AsyncConversations(list_client).list("a_1")
    assert [c.id async for c in page] == ["cv_1"]
    assert list_client.specs[-1].path == "/agents/a_1/conversations"

    send_client = FakeAsync(MESSAGE)
    msg = await AsyncConversations(send_client).send(
        "a_1", message="Hi", channel_type="webchat", channel_user_id="u_1"
    )
    assert isinstance(msg, Message)
    spec = send_client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents/a_1/conversations/messages"
    assert spec.body == {"message": "Hi", "channel_type": "webchat", "channel_user_id": "u_1"}


async def test_async_set_ai_status() -> None:
    client = FakeAsync({"is_ai_chat_paused": False})
    status = await AsyncConversations(client).set_ai_status("a_1", "cv_1", is_ai_chat_paused=False)
    assert isinstance(status, ConversationAiStatus)
    assert status.is_ai_chat_paused is False
    spec = client.specs[-1]
    assert spec.method == "PATCH"
    assert spec.path == "/agents/a_1/conversations/cv_1/ai-status"
    assert spec.body == {"is_ai_chat_paused": False}
