from typing import Any

import httpx
import pytest

from bimpeai._exceptions import APINotImplementedError
from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec
from bimpeai.resources.calls import Calls


def response(data: Any) -> ApiResponse[Any]:
    return ApiResponse(data=data, meta=None, request_id="r", status=200, headers=httpx.Headers())


class FakeRaise:
    def __init__(self) -> None:
        self.specs: list[RequestSpec] = []

    def request(self, spec: RequestSpec) -> Any:
        self.specs.append(spec)
        raise APINotImplementedError(
            "coming soon",
            status=501,
            code="not_implemented",
            request_id=None,
            headers=httpx.Headers(),
            body={},
        )


class FakeSync:
    def __init__(self, data: Any) -> None:
        self._data = data
        self.specs: list[RequestSpec] = []

    def request(self, spec: RequestSpec) -> ApiResponse[Any]:
        self.specs.append(spec)
        return response(self._data)


def test_calls_list_surfaces_not_implemented() -> None:
    client = FakeRaise()
    with pytest.raises(APINotImplementedError):
        Calls(client).list()
    assert client.specs[-1] == RequestSpec(method="GET", path="/calls")


def test_calls_make() -> None:
    client = FakeSync({"agent_id": "a_1"})
    out = Calls(client).make({"agent_id": "a_1"})
    assert out == {"agent_id": "a_1"}
    assert client.specs[-1].method == "POST"
    assert client.specs[-1].path == "/calls"


def test_calls_queue() -> None:
    client = FakeSync({"agent_id": "a_1"})
    Calls(client).queue({"agent_id": "a_1"})
    assert client.specs[-1].method == "POST"
    assert client.specs[-1].path == "/calls/queue"
