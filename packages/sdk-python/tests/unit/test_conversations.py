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


def test_list_with_channel_filter() -> None:
    conv: dict[str, Any] = {
        "id": "cv_1",
        "channel_type": "whatsapp",
        "channel_id": None,
        "is_test_channel": False,
        "full_name": None,
        "email": None,
        "phone_number": None,
        "channel_username": None,
        "is_ai_chat_paused": False,
        "last_message_at": None,
        "last_message_preview": None,
        "created_at": "t",
        "updated_at": "t",
    }
    client = FakeSync([conv])
    page = Conversations(client).list("a_1", channel="whatsapp")
    assert isinstance(page, Page)
    spec = client.specs[-1]
    assert spec.path == "/agents/a_1/conversations"
    assert spec.query == {"page": 1, "limit": None, "search": None, "channel": "whatsapp"}


def test_retrieve_and_messages_attribute() -> None:
    detail: dict[str, Any] = {
        "id": "cv_1",
        "channel_type": "whatsapp",
        "is_test_channel": False,
        "is_ai_chat_paused": False,
        "created_at": "t",
        "updated_at": "t",
    }
    client = FakeSync(detail)
    conversations = Conversations(client)
    conversations.retrieve("a_1", "cv_1")
    assert client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1/conversations/cv_1")
    assert conversations.messages is not None
