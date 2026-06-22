from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any

import httpx

from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec, StreamSpec
from bimpeai.pagination import Page
from bimpeai.resources.conversations import AsyncMessages, Messages
from bimpeai.types.conversations import Message


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


def test_list_messages_path_and_query() -> None:
    client = FakeSync(
        [{"id": "m_1", "role": "user", "message": "hi", "message_type": "text", "created_at": "t"}]
    )
    page = Messages(client).list("a_1", "cv_1", search="refund", sort="-created_at")
    assert isinstance(page, Page)
    assert page.data[0].id == "m_1"
    spec = client.specs[-1]
    assert spec.method == "GET"
    assert spec.path == "/agents/a_1/conversations/cv_1/messages"
    assert spec.query == {"page": 1, "limit": None, "search": "refund", "sort": "-created_at"}


def test_send_message_drops_attachments_from_body() -> None:
    client = FakeSync(
        {
            "id": "m_2",
            "role": "assistant",
            "message": "yo",
            "message_type": "text",
            "created_at": "t",
        }
    )
    msg = Messages(client).send(
        "a_1", "cv_1", message="Hi", role="assistant", idempotency_key="op-1"
    )
    assert isinstance(msg, Message)
    assert msg.id == "m_2"
    spec = client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents/a_1/conversations/cv_1/messages"
    assert spec.body == {"message": "Hi", "role": "assistant"}
    assert "attachments" not in spec.body
    assert spec.options.idempotency_key == "op-1"


def test_retrieve_returns_message_with_attachments() -> None:
    client = FakeSync(
        {
            "id": "m_3",
            "role": "user",
            "message": "see attachment",
            "message_type": "text",
            "created_at": "now",
            "attachments": [{"type": "image", "url": "https://x"}],
        }
    )
    msg = Messages(client).retrieve("a_1", "cv_1", "m_3")
    assert isinstance(msg, Message)
    assert msg.id == "m_3"
    assert msg.attachments is not None
    assert msg.attachments[0].url == "https://x"
    assert client.specs[-1] == RequestSpec(
        method="GET", path="/agents/a_1/conversations/cv_1/messages/m_3"
    )


async def test_async_list_send_and_retrieve() -> None:
    list_client = FakeAsync(
        [{"id": "m_1", "role": "user", "message": "hi", "message_type": "text", "created_at": "t"}]
    )
    page = await AsyncMessages(list_client).list("a_1", "cv_1")
    assert [m.id async for m in page] == ["m_1"]
    assert list_client.specs[-1].path == "/agents/a_1/conversations/cv_1/messages"

    send_client = FakeAsync(
        {
            "id": "m_2",
            "role": "assistant",
            "message": "yo",
            "message_type": "text",
            "created_at": "t",
        }
    )
    msg = await AsyncMessages(send_client).send("a_1", "cv_1", message="Hi")
    assert isinstance(msg, Message)
    spec = send_client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents/a_1/conversations/cv_1/messages"
    assert spec.body == {"message": "Hi"}

    retrieve_client = FakeAsync(
        {"id": "m_3", "role": "user", "message": "x", "message_type": "text", "created_at": "t"}
    )
    one = await AsyncMessages(retrieve_client).retrieve("a_1", "cv_1", "m_3")
    assert one.id == "m_3"
    assert retrieve_client.specs[-1] == RequestSpec(
        method="GET", path="/agents/a_1/conversations/cv_1/messages/m_3"
    )
