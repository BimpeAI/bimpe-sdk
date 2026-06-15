from typing import Any

import httpx

from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec
from bimpeai.pagination import Page
from bimpeai.resources.workflows import AsyncWorkflows, Workflows


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


def _summary(id_: str) -> dict[str, Any]:
    return {
        "id": id_,
        "name": "W",
        "description": None,
        "category": None,
        "visibility": "public",
        "is_owner": True,
        "created_at": "t",
        "updated_at": "t",
    }


def test_list_forwards_scope() -> None:
    client = FakeSync([_summary("w_1")])
    page = Workflows(client).list(scope="public")
    assert isinstance(page, Page)
    spec = client.specs[-1]
    assert spec.path == "/workflows"
    assert spec.query == {
        "page": 1,
        "limit": None,
        "search": None,
        "sort": None,
        "scope": "public",
    }


def test_crud_paths() -> None:
    detail: dict[str, Any] = {
        **_summary("w_1"),
        "system_prompt": None,
        "rules": [],
        "flows": [],
        "tags": [],
        "prompt_config": {},
    }
    client = FakeSync(detail)
    wf = Workflows(client)
    wf.create(name="Triage", idempotency_key="op-1")
    assert client.specs[-1].method == "POST"
    assert client.specs[-1].path == "/workflows"
    assert client.specs[-1].options.idempotency_key == "op-1"
    wf.retrieve("w_1")
    assert client.specs[-1] == RequestSpec(method="GET", path="/workflows/w_1")
    wf.update("w_1", tags=["v2"])
    assert client.specs[-1].body == {"tags": ["v2"]}
    wf.delete("w_1")
    assert client.specs[-1] == RequestSpec(method="DELETE", path="/workflows/w_1")


async def test_async_list() -> None:
    client = FakeAsync([_summary("w_1")])
    page = await AsyncWorkflows(client).list()
    assert [w.id async for w in page] == ["w_1"]
