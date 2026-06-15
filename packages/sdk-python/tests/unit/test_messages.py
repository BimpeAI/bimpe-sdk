from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import httpx

from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec, StreamSpec
from bimpeai.resources.conversations import Messages


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


def test_list_messages_path() -> None:
    client = FakeSync(
        [{"id": "m_1", "role": "user", "message": "hi", "message_type": "text", "created_at": "t"}]
    )
    page = Messages(client).list("a_1", "cv_1")
    assert page.data[0].id == "m_1"
    assert client.specs[-1].path == "/agents/a_1/conversations/cv_1/messages"
    assert client.specs[-1].query == {"page": 1, "limit": None}


def test_send_message() -> None:
    client = FakeSync(
        {
            "id": "m_2",
            "role": "assistant",
            "message": "yo",
            "message_type": "text",
            "created_at": "t",
        }
    )
    msg = Messages(client).send("a_1", "cv_1", message="Hi", idempotency_key="op-1")
    assert msg.id == "m_2"
    spec = client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents/a_1/conversations/cv_1/messages"
    assert spec.body == {"message": "Hi"}
    assert spec.options.idempotency_key == "op-1"
