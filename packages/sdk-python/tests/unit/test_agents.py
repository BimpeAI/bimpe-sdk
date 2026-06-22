from typing import Any

import httpx

from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec
from bimpeai.pagination import Page
from bimpeai.resources.agents import Agents, AsyncAgents
from bimpeai.types.agents import (
    AgentCreateResponse,
    AgentDetail,
    AgentLiveStatus,
    BulkActionUpdate,
    KnowledgeBaseItem,
)

AGENT: dict[str, Any] = {
    "id": "a_1",
    "name": "Bot",
    "description": "A support bot",
    "status": "live",
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


def test_create_sends_body_and_returns_create_response() -> None:
    client = FakeSync(
        {
            **AGENT,
            "name": "Hello",
            "persona": "friendly",
            "workflow_id": "wf_1",
            "workflow": {
                "id": "wf_1",
                "name": "Triage",
                "visibility": "public",
                "is_owner": True,
                "created_at": "t",
                "updated_at": "t",
            },
        }
    )
    agent = Agents(client).create(
        workflow_id="wf_1",
        name="Hello",
        description="A support agent",
        persona="friendly",
        idempotency_key="op-1",
    )
    assert isinstance(agent, AgentCreateResponse)
    assert agent.id == "a_1"
    assert agent.workflow is not None
    assert agent.workflow.id == "wf_1"
    spec = client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents"
    assert spec.body == {
        "workflow_id": "wf_1",
        "name": "Hello",
        "description": "A support agent",
        "persona": "friendly",
    }
    assert spec.options.idempotency_key == "op-1"


def test_retrieve_returns_detail_shape() -> None:
    detail: dict[str, Any] = {
        **AGENT,
        "knowledge_bases": [{"id": "k_1", "type": "text", "name": "FAQ", "description": None}],
        "integrations": [
            {
                "id": "i_1",
                "type": "slack",
                "name": "Slack",
                "status": "active",
                "is_connected": True,
            }
        ],
        "channels": [
            {
                "id": "c_1",
                "type": "whatsapp",
                "name": "WhatsApp",
                "status": "active",
                "is_connected": True,
            }
        ],
    }
    client = FakeSync(detail)
    out = Agents(client).retrieve("a_1")
    assert isinstance(out, AgentDetail)
    assert out.id == "a_1"
    assert out.knowledge_bases[0].id == "k_1"
    assert out.integrations[0].type == "slack"
    assert out.channels[0].type == "whatsapp"
    assert client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1")


def test_update_sends_patch_body() -> None:
    client = FakeSync({**AGENT, "name": "New"})
    out = Agents(client).update("a_1", name="New")
    assert out.name == "New"
    spec = client.specs[-1]
    assert spec.method == "PATCH"
    assert spec.path == "/agents/a_1"
    assert spec.body == {"name": "New"}


def test_update_live_status_patches_live_status_path() -> None:
    client = FakeSync({"status": "live", "status_reason": "launched"})
    out = Agents(client).update_live_status("a_1", status="live", status_reason="launched")
    assert isinstance(out, AgentLiveStatus)
    assert out.status == "live"
    assert out.status_reason == "launched"
    spec = client.specs[-1]
    assert spec.method == "PATCH"
    assert spec.path == "/agents/a_1/live-status"
    assert spec.body == {"status": "live", "status_reason": "launched"}


def test_integrations_subresource() -> None:
    client = FakeSync(
        [{"id": "i_1", "type": "slack", "name": "Slack", "status": "ok", "is_connected": True}]
    )
    out = Agents(client).integrations.list("a_1")
    assert out[0].type == "slack"
    assert client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1/integrations")


def test_channels_subresource() -> None:
    client = FakeSync(
        [
            {
                "id": "c_1",
                "type": "whatsapp",
                "name": "WhatsApp",
                "status": "ok",
                "is_connected": True,
            }
        ]
    )
    out = Agents(client).channels.list("a_1")
    assert out[0].type == "whatsapp"
    assert out[0].name == "WhatsApp"
    assert client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1/channels")


def test_actions_list() -> None:
    client = FakeSync(
        [
            {
                "id": "ac_1",
                "integration_id": "i_1",
                "integration_type": "slack",
                "integration_name": "Slack",
                "name": "Post",
                "action_name": "slack_post",
                "description": None,
                "is_enabled": True,
            }
        ]
    )
    out = Agents(client).actions.list("a_1")
    assert out[0].action_name == "slack_post"
    assert out[0].integration_id == "i_1"
    assert client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1/actions")


def test_actions_enable_returns_bulk_update() -> None:
    client = FakeSync({"updated_count": 2})
    out = Agents(client).actions.enable("a_1", action_ids=["ac_1", "ac_2"], idempotency_key="op-3")
    assert isinstance(out, BulkActionUpdate)
    assert out.updated_count == 2
    spec = client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents/a_1/actions/enable"
    assert spec.body == {"action_ids": ["ac_1", "ac_2"]}
    assert spec.options.idempotency_key == "op-3"


def test_actions_disable_returns_bulk_update() -> None:
    client = FakeSync({"updated_count": 1})
    out = Agents(client).actions.disable("a_1", action_ids=["ac_1"])
    assert isinstance(out, BulkActionUpdate)
    assert out.updated_count == 1
    spec = client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents/a_1/actions/disable"
    assert spec.body == {"action_ids": ["ac_1"]}


def test_knowledge_bases_crud() -> None:
    kb = {"id": "k_1", "type": "text", "name": "FAQ", "description": None, "content": "x"}
    client = FakeSync(kb)
    agents = Agents(client)

    created = agents.knowledge_bases.create(
        "a_1", {"type": "text", "name": "FAQ", "content": "x"}, idempotency_key="op-2"
    )
    assert isinstance(created, KnowledgeBaseItem)
    assert created.content == "x"
    create_spec = client.specs[-1]
    assert create_spec.method == "POST"
    assert create_spec.path == "/agents/a_1/knowledge_bases"
    assert create_spec.body == {"type": "text", "name": "FAQ", "content": "x"}
    assert create_spec.options.idempotency_key == "op-2"

    updated = agents.knowledge_bases.update("a_1", "k_1", name="New")
    assert isinstance(updated, KnowledgeBaseItem)
    update_spec = client.specs[-1]
    assert update_spec.method == "PATCH"
    assert update_spec.path == "/agents/a_1/knowledge_bases/k_1"
    assert update_spec.body == {"name": "New"}

    agents.knowledge_bases.delete("a_1", "k_1")
    assert client.specs[-1] == RequestSpec(method="DELETE", path="/agents/a_1/knowledge_bases/k_1")


def test_knowledge_bases_list_returns_items() -> None:
    client = FakeSync(
        [
            {
                "id": "k_1",
                "type": "text",
                "name": "FAQ",
                "description": None,
                "url": None,
                "content": "hello",
            }
        ]
    )
    out = Agents(client).knowledge_bases.list("a_1")
    assert isinstance(out[0], KnowledgeBaseItem)
    assert out[0].content == "hello"
    assert client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1/knowledge_bases")


async def test_async_list_and_create() -> None:
    client = FakeAsync([AGENT])
    page = await AsyncAgents(client).list()
    assert [agent.id async for agent in page] == ["a_1"]

    create_client = FakeAsync(
        {
            **AGENT,
            "name": "Hi",
            "workflow_id": "wf_1",
            "workflow": {
                "id": "wf_1",
                "name": "Triage",
                "visibility": "public",
                "is_owner": True,
                "created_at": "t",
                "updated_at": "t",
            },
        }
    )
    created = await AsyncAgents(create_client).create(
        workflow_id="wf_1", name="Hi", description="An agent"
    )
    assert isinstance(created, AgentCreateResponse)
    assert created.workflow is not None
    assert created.workflow.id == "wf_1"
    spec = create_client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents"
    assert spec.body == {"workflow_id": "wf_1", "name": "Hi", "description": "An agent"}


async def test_async_retrieve_and_actions() -> None:
    detail_client = FakeAsync(
        {**AGENT, "knowledge_bases": [], "integrations": [], "channels": []}
    )
    detail = await AsyncAgents(detail_client).retrieve("a_1")
    assert isinstance(detail, AgentDetail)
    assert detail_client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1")

    enable_client = FakeAsync({"updated_count": 3})
    out = await AsyncAgents(enable_client).actions.enable(
        "a_1", action_ids=["ac_1", "ac_2", "ac_3"]
    )
    assert isinstance(out, BulkActionUpdate)
    assert out.updated_count == 3
    spec = enable_client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents/a_1/actions/enable"
    assert spec.body == {"action_ids": ["ac_1", "ac_2", "ac_3"]}


async def test_async_update_live_status() -> None:
    client = FakeAsync({"status": "paused", "status_reason": None})
    out = await AsyncAgents(client).update_live_status("a_1", status="paused")
    assert isinstance(out, AgentLiveStatus)
    assert out.status == "paused"
    spec = client.specs[-1]
    assert spec.method == "PATCH"
    assert spec.path == "/agents/a_1/live-status"
    assert spec.body == {"status": "paused"}
