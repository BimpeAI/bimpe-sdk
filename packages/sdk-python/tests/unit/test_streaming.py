import time
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any

import httpx
import pytest

from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec, StreamSpec
from bimpeai.resources.conversations import AsyncMessages, Messages

MSG_1 = b'id: m_1\nevent: message\ndata: {"id":"m_1","conversation_id":"cv_1","role":"user","message":"hi","message_type":"text","created_at":"t"}\n\n'  # noqa: E501
HEARTBEAT = b'event: heartbeat\ndata: {"ts":1}\n\n'
MSG_2 = b'id: m_2\nevent: message\ndata: {"id":"m_2","conversation_id":"cv_1","role":"assistant","message":"yo","message_type":"text","created_at":"t"}\n\n'  # noqa: E501


def _sse(body: bytes) -> httpx.Response:
    return httpx.Response(
        200,
        content=body,
        headers={"content-type": "text/event-stream"},
        request=httpx.Request("GET", "https://x"),
    )


class FakeSync:
    def __init__(self, bodies: list[bytes]) -> None:
        self._bodies = list(bodies)
        self.stream_specs: list[StreamSpec] = []

    def request(self, spec: RequestSpec) -> ApiResponse[Any]:
        return ApiResponse(
            data={"ticket": "t1", "expires_in": 60},
            meta=None,
            request_id="r",
            status=201,
            headers=httpx.Headers(),
        )

    @contextmanager
    def stream(self, spec: StreamSpec) -> Generator[httpx.Response, None, None]:
        self.stream_specs.append(spec)
        yield _sse(self._bodies.pop(0))


def test_yields_messages_and_skips_heartbeats() -> None:
    client = FakeSync([MSG_1 + HEARTBEAT + MSG_2])
    ids = [event.id for event in Messages(client).stream("a_1", "cv_1", reconnect=False)]
    assert ids == ["m_1", "m_2"]


def test_reconnect_resumes_from_last_id(monkeypatch: pytest.MonkeyPatch) -> None:
    def _no_sleep(_seconds: float) -> None:
        return None

    monkeypatch.setattr(time, "sleep", _no_sleep)
    client = FakeSync([MSG_1, MSG_2])
    ids: list[str] = []
    for event in Messages(client).stream("a_1", "cv_1"):
        ids.append(event.id)
        if len(ids) == 2:
            break
    assert ids == ["m_1", "m_2"]
    assert client.stream_specs[1].query == {"ticket": "t1", "after": "m_1"}


class FakeAsync:
    def __init__(self, bodies: list[bytes]) -> None:
        self._bodies = list(bodies)

    async def request(self, spec: RequestSpec) -> ApiResponse[Any]:
        return ApiResponse(
            data={"ticket": "t1", "expires_in": 60},
            meta=None,
            request_id="r",
            status=201,
            headers=httpx.Headers(),
        )

    @asynccontextmanager
    async def stream(self, spec: StreamSpec) -> AsyncGenerator[httpx.Response, None]:
        yield _sse(self._bodies.pop(0))


async def test_async_yields_messages() -> None:
    client = FakeAsync([MSG_1 + HEARTBEAT + MSG_2])
    ids = [event.id async for event in AsyncMessages(client).stream("a_1", "cv_1", reconnect=False)]
    assert ids == ["m_1", "m_2"]
