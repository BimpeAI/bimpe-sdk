from typing import Any

import httpx

from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec
from bimpeai.pagination import Page
from bimpeai.resources.agents import Agents, AsyncAgents
from bimpeai.types.agents import Agent

AGENT: dict[str, Any] = {
    "id": "a_1",
    "name": "Bot",
    "status": "active",
    "created_at": "t",
    "updated_at": "t",
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


def test_list_builds_get_with_query_and_returns_page() -> None:
    client = FakeSync([AGENT])
    page = Agents(client).list(page=1, limit=50, sort="-created_at")
    assert isinstance(page, Page)
    assert page.data[0].id == "a_1"
    spec = client.specs[-1]
    assert spec.method == "GET"
    assert spec.path == "/agents"
    assert spec.query == {"page": 1, "limit": 50, "search": None, "sort": "-created_at"}


def test_create_sends_body_and_idempotency() -> None:
    client = FakeSync({**AGENT, "name": "Hi"})
    agent = Agents(client).create(name="Hi", idempotency_key="op-1")
    assert isinstance(agent, Agent)
    spec = client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents"
    assert spec.body == {"name": "Hi"}
    assert spec.options.idempotency_key == "op-1"


def test_retrieve_and_update() -> None:
    detail: dict[str, Any] = {
        **AGENT,
        "integration": [],
        "channel": [],
        "conversation_flow": [],
        "actions": [],
        "knowledge_bases": [],
    }
    client = FakeSync(detail)
    Agents(client).retrieve("a_1")
    assert client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1")
    Agents(FakeSync({**AGENT, "name": "New"})).update("a_1", name="New")


def test_integrations_subresource() -> None:
    client = FakeSync([{"id": "i_1", "type": "slack", "status": "ok", "is_connected": True}])
    out = Agents(client).integrations.list("a_1")
    assert out[0].type == "slack"
    assert client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1/integrations")


def test_knowledge_bases_crud() -> None:
    kb = {"id": "k_1", "type": "text", "name": "FAQ", "description": None}
    client = FakeSync(kb)
    agents = Agents(client)
    agents.knowledge_bases.create(
        "a_1", {"type": "text", "name": "FAQ", "content": "x"}, idempotency_key="op-2"
    )
    create_spec = client.specs[-1]
    assert create_spec.method == "POST"
    assert create_spec.path == "/agents/a_1/knowledge_bases"
    assert create_spec.body == {"type": "text", "name": "FAQ", "content": "x"}
    assert create_spec.options.idempotency_key == "op-2"
    agents.knowledge_bases.delete("a_1", "k_1")
    assert client.specs[-1] == RequestSpec(method="DELETE", path="/agents/a_1/knowledge_bases/k_1")


async def test_async_list_and_create() -> None:
    client = FakeAsync([AGENT])
    page = await AsyncAgents(client).list()
    assert [agent.id async for agent in page] == ["a_1"]
    create_client = FakeAsync({**AGENT, "name": "Hi"})
    await AsyncAgents(create_client).create(name="Hi")
    assert create_client.specs[-1].method == "POST"
