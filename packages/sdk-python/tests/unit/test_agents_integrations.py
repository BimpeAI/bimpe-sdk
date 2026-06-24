from typing import Any

import httpx

from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec
from bimpeai.resources.agents import Agents, AsyncAgents
from bimpeai.types.agents import (
    AgentTestCode,
    BimpeaiIntegration,
    CustomApiIntegration,
    IntegrationTool,
    McpServerDiscoverResult,
    McpServerIntegration,
    McpServerTestResult,
    OnboardingUrl,
)

TEST_CODE: dict[str, Any] = {
    "code": "ABC123XY",
    "channels": {
        "whatsapp": {"is_enabled": True, "start_message": "start ABC123XY"},
        "instagram": {"is_enabled": True, "start_message": "start ABC123XY"},
        "messenger": {"is_enabled": False, "start_message": "start ABC123XY"},
        "telephony": {"is_enabled": True},
    },
}

BIMPEAI_ITEM: dict[str, Any] = {
    "id": "ch_1",
    "type": "stripe",
    "name": "Stripe",
    "status": "enabled",
    "is_connected": True,
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


def test_get_test_code_gets_deployment_endpoint() -> None:
    client = FakeSync(TEST_CODE)
    out = Agents(client).get_test_code("a_1")
    assert isinstance(out, AgentTestCode)
    assert out.code == "ABC123XY"
    assert out.channels.whatsapp.is_enabled is True
    assert out.channels.messenger.is_enabled is False
    assert client.specs[-1] == RequestSpec(
        method="GET", path="/agents/a_1/deployment/agent-test-code"
    )


def test_bimpeai_list_gets_endpoint() -> None:
    client = FakeSync([BIMPEAI_ITEM])
    out = Agents(client).integrations.bimpeai.list("a_1")
    assert isinstance(out[0], BimpeaiIntegration)
    assert out[0].type == "stripe"
    assert out[0].is_connected is True
    assert client.specs[-1] == RequestSpec(method="GET", path="/agents/a_1/integrations/bimpeai")


def test_bimpeai_configure_posts_and_returns_onboarding_url() -> None:
    client = FakeSync({"onboarding_url": "https://agent.bimpe.ai/connect"})
    out = Agents(client).integrations.bimpeai.configure(
        "a_1",
        type="stripe",
        public_key="pk",
        secret_key="sk",
        currency="NGN",
        idempotency_key="op-1",
    )
    assert isinstance(out, OnboardingUrl)
    assert out.onboarding_url == "https://agent.bimpe.ai/connect"
    spec = client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents/a_1/integrations/bimpeai/configure"
    assert spec.body == {
        "type": "stripe",
        "public_key": "pk",
        "secret_key": "sk",
        "currency": "NGN",
    }
    assert spec.options.idempotency_key == "op-1"


def test_bimpeai_disconnect_deletes() -> None:
    client = FakeSync({"message": "ok"})
    out = Agents(client).integrations.bimpeai.disconnect("a_1", "ch_1")
    assert out is None
    assert client.specs[-1] == RequestSpec(
        method="DELETE", path="/agents/a_1/integrations/bimpeai/ch_1"
    )


async def test_async_bimpeai_and_test_code() -> None:
    code_client = FakeAsync(TEST_CODE)
    code = await AsyncAgents(code_client).get_test_code("a_1")
    assert code.code == "ABC123XY"
    assert code_client.specs[-1].path == "/agents/a_1/deployment/agent-test-code"

    list_client = FakeAsync([BIMPEAI_ITEM])
    items = await AsyncAgents(list_client).integrations.bimpeai.list("a_1")
    assert items[0].type == "stripe"

    cfg_client = FakeAsync({"onboarding_url": "https://x"})
    cfg = await AsyncAgents(cfg_client).integrations.bimpeai.configure(
        "a_1", type="google_calendar"
    )
    assert cfg.onboarding_url == "https://x"
    assert cfg_client.specs[-1].path == "/agents/a_1/integrations/bimpeai/configure"


def test_custom_api_configure_and_tools() -> None:
    cfg_client = FakeSync({"id": "ci_1", "config": {"name": "Shop", "auth_type": "none"}})
    cfg = Agents(cfg_client).integrations.custom_api.configure(
        "a_1", name="Shop", base_url="https://api.example.com"
    )
    assert isinstance(cfg, CustomApiIntegration)
    assert cfg.config.name == "Shop"
    spec = cfg_client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/agents/a_1/integrations/custom_api/configure"
    assert spec.body == {"name": "Shop", "base_url": "https://api.example.com"}

    tool_client = FakeSync(
        {
            "id": "t_1",
            "action_name": "create_order",
            "name": "Create Order",
            "description": None,
            "category": "custom",
            "is_enabled": True,
        }
    )
    tool = Agents(tool_client).integrations.custom_api.tools.add(
        "a_1",
        "ci_1",
        {"name": "Create Order", "http_method": "POST", "url_template": "/orders"},
    )
    assert isinstance(tool, IntegrationTool)
    assert tool.action_name == "create_order"
    assert tool_client.specs[-1].path == "/agents/a_1/integrations/custom_api/ci_1/tools"

    del_client = FakeSync({"message": "ok"})
    assert Agents(del_client).integrations.custom_api.tools.delete("a_1", "ci_1", "t_1") is None
    assert del_client.specs[-1] == RequestSpec(
        method="DELETE", path="/agents/a_1/integrations/custom_api/ci_1/tools/t_1"
    )


def test_mcp_server_configure_discover_test() -> None:
    cfg_client = FakeSync(
        {
            "id": "m_1",
            "config": {
                "name": "MR",
                "server_url": "https://x",
                "transport": "streamable_http",
                "auth_type": "none",
            },
        }
    )
    cfg = Agents(cfg_client).integrations.mcp_server.configure(
        "a_1", name="MR", server_url="https://x"
    )
    assert isinstance(cfg, McpServerIntegration)
    assert cfg.config.transport == "streamable_http"

    disc_client = FakeSync({"discovered": 3, "created": 2, "updated": 1, "disabled": 0})
    disc = Agents(disc_client).integrations.mcp_server.discover("a_1", "m_1")
    assert isinstance(disc, McpServerDiscoverResult)
    assert disc.discovered == 3
    assert disc_client.specs[-1] == RequestSpec(
        method="POST", path="/agents/a_1/integrations/mcp_server/m_1/discover"
    )

    test_client = FakeSync({"success": True, "message": "ok"})
    result = Agents(test_client).integrations.mcp_server.test("a_1", "m_1")
    assert isinstance(result, McpServerTestResult)
    assert result.success is True
    assert test_client.specs[-1].path == "/agents/a_1/integrations/mcp_server/m_1/test"


def test_pipedream_configure_and_disconnect() -> None:
    cfg_client = FakeSync({"onboarding_url": "https://agent.bimpe.ai/connect"})
    cfg = Agents(cfg_client).integrations.pipedream.configure("a_1", app_slug="google-sheets")
    assert isinstance(cfg, OnboardingUrl)
    assert cfg.onboarding_url.endswith("connect")
    assert cfg_client.specs[-1].body == {"app_slug": "google-sheets"}

    del_client = FakeSync({"message": "ok"})
    assert Agents(del_client).integrations.pipedream.disconnect("a_1", "p_1") is None
    assert del_client.specs[-1] == RequestSpec(
        method="DELETE", path="/agents/a_1/integrations/pipedream/p_1"
    )


async def test_async_phase2() -> None:
    cfg_client = FakeAsync(
        {
            "id": "m_1",
            "config": {
                "name": "MR",
                "server_url": "https://x",
                "transport": "http_sse",
                "auth_type": "none",
            },
        }
    )
    cfg = await AsyncAgents(cfg_client).integrations.mcp_server.configure(
        "a_1", name="MR", server_url="https://x"
    )
    assert cfg.config.transport == "http_sse"

    tools_client = FakeAsync(
        [
            {
                "id": "t_1",
                "action_name": "search",
                "name": "Search",
                "description": None,
                "category": "mcp",
                "is_enabled": True,
            }
        ]
    )
    tools = await AsyncAgents(tools_client).integrations.mcp_server.tools.list("a_1", "m_1")
    assert tools[0].action_name == "search"
    assert tools_client.specs[-1].path == "/agents/a_1/integrations/mcp_server/m_1/tools"
