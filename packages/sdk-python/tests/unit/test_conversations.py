from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import httpx

from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec, StreamSpec
from bimpeai.pagination import Page
from bimpeai.resources.conversations import Conversations


class FakeSync:
    def __init__(self, data: Any) -> None:
        self._data = data
        self.specs: list[RequestSpec] = []

    def request(self, spec: RequestSpec) -> ApiResponse[Any]:
        self.specs.append(spec)
        return ApiResponse(
            data=self._data, meta=None, request_id="r", status=200, headers=httpx.Headers()
        )

    @contextmanager
    def stream(self, spec: StreamSpec) -> Generator[httpx.Response, None, None]:
        yield httpx.Response(200, content=b"", request=httpx.Request("GET", "https://x"))


def _list_item() -> dict[str, Any]:
    return {
        "id": "cv_1",
        "channel_type": "whatsapp",
        "channel_id": None,
        "channel_user_id": "+2348012345678",
        "channel_user_username": None,
        "is_test_channel": False,
        "is_ai_chat_paused": False,
        "needs_attention": False,
        "last_message_at": None,
        "last_seen": None,
        "last_message_preview": None,
        "created_at": "t",
        "updated_at": "t",
    }


def test_list_with_filters() -> None:
    client = FakeSync([_list_item()])
    page = Conversations(client).list(
        "a_1",
        channel="whatsapp",
        is_test_channel=False,
        needs_attention=True,
    )
    assert isinstance(page, Page)
    spec = client.specs[-1]
    assert spec.path == "/agents/a_1/conversations"
    assert spec.query == {
        "page": 1,
        "limit": None,
        "search": None,
        "channel": "whatsapp",
        "is_test_channel": False,
        "is_ai_chat_paused": None,
        "needs_attention": True,
    }


def test_retrieve_and_messages_attribute() -> None:
    detail: dict[str, Any] = {
        **_list_item(),
        "full_name": None,
        "email": None,
        "phone_number": None,
        "profile_picture": None,
    }
    client = FakeSync(detail)
    conversations = Conversations(client)
    conversations.retrieve("a_1", "cv_1")
    assert client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1/conversations/cv_1")
    assert conversations.messages is not None


def test_create_or_send_mode_a() -> None:
    client = FakeSync(
        {
            "id": "m_1",
            "role": "user",
            "message": "Hi",
            "message_type": "text",
            "created_at": "t",
            "conversation_id": "cv_1",
        }
    )
    out = Conversations(client).create_or_send(
        "a_1",
        {"conversation_id": "cv_1", "message": "Hi"},
        idempotency_key="op-1",
    )
    assert out.conversation_id == "cv_1"
    assert client.specs[-1] == RequestSpec(
        method="POST",
        path="/agents/a_1/conversations/messages",
        body={"conversation_id": "cv_1", "message": "Hi"},
        options=client.specs[-1].options,
    )


def test_create_or_send_mode_b() -> None:
    client = FakeSync(
        {
            "id": "m_1",
            "role": "user",
            "message": "Hi",
            "message_type": "text",
            "created_at": "t",
            "conversation_id": "cv_new",
        }
    )
    Conversations(client).create_or_send(
        "a_1",
        {
            "message": "Hi",
            "channel_type": "whatsapp",
            "channel_user_id": "+2348012345678",
        },
    )
    assert client.specs[-1].body == {
        "message": "Hi",
        "channel_type": "whatsapp",
        "channel_user_id": "+2348012345678",
    }


def test_update_ai_status() -> None:
    client = FakeSync({"is_ai_chat_paused": True})
    out = Conversations(client).update_ai_status("a_1", "cv_1", is_ai_chat_paused=True)
    assert out.is_ai_chat_paused is True
    assert client.specs[-1] == RequestSpec(
        method="PATCH",
        path="/agents/a_1/conversations/cv_1/ai-status",
        body={"is_ai_chat_paused": True},
    )
