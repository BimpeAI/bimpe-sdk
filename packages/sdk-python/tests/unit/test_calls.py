from typing import Any

import httpx

from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec
from bimpeai.pagination import Page
from bimpeai.resources.calls import AsyncCalls, Calls
from bimpeai.types.calls import CallDetail, MakeCallResult

CALL: dict[str, Any] = {
    "id": "call_1",
    "source": None,
    "destination": "+15551234567",
    "status": "ended",
    "direction": "outbound",
    "created_on": "now",
    "duration_seconds": 42,
    "is_test_call": False,
    "error_reason": None,
    "end_reason": "completed",
    "ringing_at": None,
    "ended_at": "now",
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


class FakeAsync:
    def __init__(self, data: Any) -> None:
        self._data = data
        self.specs: list[RequestSpec] = []

    async def request(self, spec: RequestSpec) -> ApiResponse[Any]:
        self.specs.append(spec)
        return response(self._data)


def test_list_builds_agent_scoped_get_and_returns_page() -> None:
    client = FakeSync([CALL])
    page = Calls(client).list("a_1", status="ended", is_test_call=False)
    assert isinstance(page, Page)
    assert page.data[0].id == "call_1"
    assert page.data[0].status == "ended"
    spec = client.specs[-1]
    assert spec.method == "GET"
    assert spec.path == "/agents/a_1/calls"
    assert spec.query == {
        "page": 1,
        "limit": None,
        "search": None,
        "sort": None,
        "is_test_call": False,
        "status": "ended",
    }


def test_make_posts_agent_scoped_path_and_returns_result() -> None:
    client = FakeSync({"status": "initiated", "call_id": "call_1", "detail": "dialing"})
    result = Calls(client).make(
        "a_1",
        {"destination": "+15551234567", "is_test_call": False},
        idempotency_key="op-1",
    )
    assert isinstance(result, MakeCallResult)
    assert result.status == "initiated"
    assert result.call_id == "call_1"
    assert result.detail == "dialing"
    spec = client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents/a_1/calls"
    assert spec.body == {"destination": "+15551234567", "is_test_call": False}
    assert spec.options.idempotency_key == "op-1"


def test_retrieve_returns_detail_shape() -> None:
    detail: dict[str, Any] = {
        **CALL,
        "started_at": "now",
        "answered_at": "now",
        "conversation_logs": [
            {
                "id": "log_1",
                "role": "assistant",
                "message": "Hello",
                "message_type": "text",
                "created_at": "now",
            }
        ],
    }
    client = FakeSync(detail)
    out = Calls(client).retrieve("a_1", "call_1")
    assert isinstance(out, CallDetail)
    assert out.id == "call_1"
    assert out.conversation_logs[0].id == "log_1"
    assert client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1/calls/call_1")


async def test_async_list_and_make() -> None:
    list_client = FakeAsync([CALL])
    page = await AsyncCalls(list_client).list("a_1")
    assert [call.id async for call in page] == ["call_1"]
    assert list_client.specs[-1].path == "/agents/a_1/calls"

    make_client = FakeAsync({"status": "busy", "call_id": None, "detail": "line busy"})
    result = await AsyncCalls(make_client).make(
        "a_1", {"destination": "+15551230000", "is_test_call": True}
    )
    assert isinstance(result, MakeCallResult)
    assert result.status == "busy"
    spec = make_client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents/a_1/calls"
    assert spec.body == {"destination": "+15551230000", "is_test_call": True}
