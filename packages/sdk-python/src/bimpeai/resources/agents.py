from __future__ import annotations

from typing import Any

from typing_extensions import Unpack

from .._request import RequestOptions
from ..pagination import AsyncPage, Page
from ..types.agents import (
    Agent,
    AgentAction,
    AgentChannel,
    AgentCreateResponse,
    AgentDetail,
    AgentIntegration,
    AgentLiveStatus,
    AgentTestCode,
    BimpeaiConfigureBody,
    BimpeaiIntegration,
    BulkActionIdsBody,
    BulkActionUpdate,
    CreateAgentBody,
    CreateKnowledgeBaseBody,
    CustomApiConfigureBody,
    CustomApiCreateToolBody,
    CustomApiIntegration,
    IntegrationTool,
    KnowledgeBaseItem,
    McpServerConfigureBody,
    McpServerDiscoverResult,
    McpServerIntegration,
    McpServerTestResult,
    OnboardingUrl,
    PipedreamConfigureBody,
    PipedreamIntegration,
    UpdateAgentBody,
    UpdateKnowledgeBaseBody,
    UpdateLiveStatusBody,
)
from ._specs import (
    AsyncTransport,
    SyncTransport,
    add_custom_api_tool_spec,
    configure_bimpeai_integration_spec,
    configure_custom_api_integration_spec,
    configure_mcp_server_integration_spec,
    configure_pipedream_integration_spec,
    create_agent_spec,
    create_knowledge_base_spec,
    delete_agent_spec,
    delete_custom_api_tool_spec,
    delete_knowledge_base_spec,
    disable_actions_spec,
    disconnect_bimpeai_integration_spec,
    disconnect_custom_api_integration_spec,
    disconnect_mcp_server_integration_spec,
    disconnect_pipedream_integration_spec,
    discover_mcp_server_tools_spec,
    enable_actions_spec,
    get_test_code_spec,
    list_agent_subresource_spec,
    list_agents_spec,
    list_bimpeai_integrations_spec,
    list_custom_api_integrations_spec,
    list_custom_api_tools_spec,
    list_mcp_server_integrations_spec,
    list_mcp_server_tools_spec,
    list_pipedream_integrations_spec,
    retrieve_agent_spec,
    test_mcp_server_connection_spec,
    update_agent_spec,
    update_knowledge_base_spec,
    update_live_status_spec,
)


class Agents:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client
        self.integrations = _AgentIntegrations(client)
        self.channels = _AgentChannels(client)
        self.actions = _AgentActions(client)
        self.knowledge_bases = _AgentKnowledgeBases(client)

    def list(
        self,
        *,
        page: int = 1,
        limit: int | None = None,
        search: str | None = None,
        sort: str | None = None,
    ) -> Page[Agent]:
        def fetch(current: int) -> Page[Agent]:
            resp = self._client.request(
                list_agents_spec(page=current, limit=limit, search=search, sort=sort)
            )
            data = [Agent.model_validate(item) for item in resp.data]
            return Page(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return fetch(page)

    def create(
        self,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[CreateAgentBody],
    ) -> AgentCreateResponse:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(create_agent_spec(dict(body), options))
        return AgentCreateResponse.model_validate(resp.data)

    def retrieve(self, agent_id: str) -> AgentDetail:
        resp = self._client.request(retrieve_agent_spec(agent_id))
        return AgentDetail.model_validate(resp.data)

    def update(self, agent_id: str, **body: Unpack[UpdateAgentBody]) -> Agent:
        resp = self._client.request(update_agent_spec(agent_id, dict(body)))
        return Agent.model_validate(resp.data)

    def delete(self, agent_id: str) -> None:
        self._client.request(delete_agent_spec(agent_id))

    def update_live_status(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[UpdateLiveStatusBody],
    ) -> AgentLiveStatus:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(update_live_status_spec(agent_id, dict(body), options))
        return AgentLiveStatus.model_validate(resp.data)

    def get_test_code(self, agent_id: str) -> AgentTestCode:
        resp = self._client.request(get_test_code_spec(agent_id))
        return AgentTestCode.model_validate(resp.data)


class _AgentBimpeaiIntegrations:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self, agent_id: str) -> list[BimpeaiIntegration]:
        resp = self._client.request(list_bimpeai_integrations_spec(agent_id))
        return [BimpeaiIntegration.model_validate(item) for item in resp.data]

    def configure(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[BimpeaiConfigureBody],
    ) -> OnboardingUrl:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(
            configure_bimpeai_integration_spec(agent_id, dict(body), options)
        )
        return OnboardingUrl.model_validate(resp.data)

    def disconnect(self, agent_id: str, integration_id: str) -> None:
        self._client.request(disconnect_bimpeai_integration_spec(agent_id, integration_id))


class _AgentCustomApiTools:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self, agent_id: str, integration_id: str) -> list[IntegrationTool]:
        resp = self._client.request(list_custom_api_tools_spec(agent_id, integration_id))
        return [IntegrationTool.model_validate(item) for item in resp.data]

    def add(
        self,
        agent_id: str,
        integration_id: str,
        body: CustomApiCreateToolBody,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> IntegrationTool:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(
            add_custom_api_tool_spec(agent_id, integration_id, dict(body), options)
        )
        return IntegrationTool.model_validate(resp.data)

    def delete(self, agent_id: str, integration_id: str, tool_id: str) -> None:
        self._client.request(delete_custom_api_tool_spec(agent_id, integration_id, tool_id))


class _AgentCustomApiIntegrations:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client
        self.tools = _AgentCustomApiTools(client)

    def list(self, agent_id: str) -> list[CustomApiIntegration]:
        resp = self._client.request(list_custom_api_integrations_spec(agent_id))
        return [CustomApiIntegration.model_validate(item) for item in resp.data]

    def configure(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[CustomApiConfigureBody],
    ) -> CustomApiIntegration:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(
            configure_custom_api_integration_spec(agent_id, dict(body), options)
        )
        return CustomApiIntegration.model_validate(resp.data)

    def disconnect(self, agent_id: str, integration_id: str) -> None:
        self._client.request(disconnect_custom_api_integration_spec(agent_id, integration_id))


class _AgentMcpServerTools:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self, agent_id: str, integration_id: str) -> list[IntegrationTool]:
        resp = self._client.request(list_mcp_server_tools_spec(agent_id, integration_id))
        return [IntegrationTool.model_validate(item) for item in resp.data]


class _AgentMcpServerIntegrations:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client
        self.tools = _AgentMcpServerTools(client)

    def list(self, agent_id: str) -> list[McpServerIntegration]:
        resp = self._client.request(list_mcp_server_integrations_spec(agent_id))
        return [McpServerIntegration.model_validate(item) for item in resp.data]

    def configure(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[McpServerConfigureBody],
    ) -> McpServerIntegration:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(
            configure_mcp_server_integration_spec(agent_id, dict(body), options)
        )
        return McpServerIntegration.model_validate(resp.data)

    def disconnect(self, agent_id: str, integration_id: str) -> None:
        self._client.request(disconnect_mcp_server_integration_spec(agent_id, integration_id))

    def discover(self, agent_id: str, integration_id: str) -> McpServerDiscoverResult:
        resp = self._client.request(discover_mcp_server_tools_spec(agent_id, integration_id))
        return McpServerDiscoverResult.model_validate(resp.data)

    def test(self, agent_id: str, integration_id: str) -> McpServerTestResult:
        resp = self._client.request(test_mcp_server_connection_spec(agent_id, integration_id))
        return McpServerTestResult.model_validate(resp.data)


class _AgentPipedreamIntegrations:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self, agent_id: str) -> list[PipedreamIntegration]:
        resp = self._client.request(list_pipedream_integrations_spec(agent_id))
        return [PipedreamIntegration.model_validate(item) for item in resp.data]

    def configure(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[PipedreamConfigureBody],
    ) -> OnboardingUrl:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(
            configure_pipedream_integration_spec(agent_id, dict(body), options)
        )
        return OnboardingUrl.model_validate(resp.data)

    def disconnect(self, agent_id: str, integration_id: str) -> None:
        self._client.request(disconnect_pipedream_integration_spec(agent_id, integration_id))


class _AgentIntegrations:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client
        self.bimpeai = _AgentBimpeaiIntegrations(client)
        self.custom_api = _AgentCustomApiIntegrations(client)
        self.mcp_server = _AgentMcpServerIntegrations(client)
        self.pipedream = _AgentPipedreamIntegrations(client)

    def list(self, agent_id: str) -> list[AgentIntegration]:
        resp = self._client.request(list_agent_subresource_spec(agent_id, "integrations"))
        return [AgentIntegration.model_validate(item) for item in resp.data]


class _AgentChannels:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self, agent_id: str) -> list[AgentChannel]:
        resp = self._client.request(list_agent_subresource_spec(agent_id, "channels"))
        return [AgentChannel.model_validate(item) for item in resp.data]


class _AgentActions:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self, agent_id: str) -> list[AgentAction]:
        resp = self._client.request(list_agent_subresource_spec(agent_id, "actions"))
        return [AgentAction.model_validate(item) for item in resp.data]

    def enable(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[BulkActionIdsBody],
    ) -> BulkActionUpdate:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(enable_actions_spec(agent_id, dict(body), options))
        return BulkActionUpdate.model_validate(resp.data)

    def disable(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[BulkActionIdsBody],
    ) -> BulkActionUpdate:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(disable_actions_spec(agent_id, dict(body), options))
        return BulkActionUpdate.model_validate(resp.data)


class _AgentKnowledgeBases:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self, agent_id: str) -> list[KnowledgeBaseItem]:
        resp = self._client.request(list_agent_subresource_spec(agent_id, "knowledge_bases"))
        return [KnowledgeBaseItem.model_validate(item) for item in resp.data]

    def create(
        self,
        agent_id: str,
        body: CreateKnowledgeBaseBody,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> KnowledgeBaseItem:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(create_knowledge_base_spec(agent_id, dict(body), options))
        return KnowledgeBaseItem.model_validate(resp.data)

    def update(
        self, agent_id: str, kb_id: str, **body: Unpack[UpdateKnowledgeBaseBody]
    ) -> KnowledgeBaseItem:
        resp = self._client.request(update_knowledge_base_spec(agent_id, kb_id, dict(body)))
        return KnowledgeBaseItem.model_validate(resp.data)

    def delete(self, agent_id: str, kb_id: str) -> None:
        self._client.request(delete_knowledge_base_spec(agent_id, kb_id))


class AsyncAgents:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client
        self.integrations = _AsyncAgentIntegrations(client)
        self.channels = _AsyncAgentChannels(client)
        self.actions = _AsyncAgentActions(client)
        self.knowledge_bases = _AsyncAgentKnowledgeBases(client)

    async def list(
        self,
        *,
        page: int = 1,
        limit: int | None = None,
        search: str | None = None,
        sort: str | None = None,
    ) -> AsyncPage[Agent]:
        async def fetch(current: int) -> AsyncPage[Agent]:
            resp = await self._client.request(
                list_agents_spec(page=current, limit=limit, search=search, sort=sort)
            )
            data = [Agent.model_validate(item) for item in resp.data]
            return AsyncPage(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return await fetch(page)

    async def create(
        self,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[CreateAgentBody],
    ) -> AgentCreateResponse:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(create_agent_spec(dict(body), options))
        return AgentCreateResponse.model_validate(resp.data)

    async def retrieve(self, agent_id: str) -> AgentDetail:
        resp = await self._client.request(retrieve_agent_spec(agent_id))
        return AgentDetail.model_validate(resp.data)

    async def update(self, agent_id: str, **body: Unpack[UpdateAgentBody]) -> Agent:
        resp = await self._client.request(update_agent_spec(agent_id, dict(body)))
        return Agent.model_validate(resp.data)

    async def delete(self, agent_id: str) -> None:
        await self._client.request(delete_agent_spec(agent_id))

    async def update_live_status(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[UpdateLiveStatusBody],
    ) -> AgentLiveStatus:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(update_live_status_spec(agent_id, dict(body), options))
        return AgentLiveStatus.model_validate(resp.data)

    async def get_test_code(self, agent_id: str) -> AgentTestCode:
        resp = await self._client.request(get_test_code_spec(agent_id))
        return AgentTestCode.model_validate(resp.data)


async def _alist_sub(client: AsyncTransport, agent_id: str, name: str) -> list[Any]:
    resp = await client.request(list_agent_subresource_spec(agent_id, name))
    return list(resp.data)


class _AsyncAgentBimpeaiIntegrations:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self, agent_id: str) -> list[BimpeaiIntegration]:
        resp = await self._client.request(list_bimpeai_integrations_spec(agent_id))
        return [BimpeaiIntegration.model_validate(item) for item in resp.data]

    async def configure(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[BimpeaiConfigureBody],
    ) -> OnboardingUrl:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(
            configure_bimpeai_integration_spec(agent_id, dict(body), options)
        )
        return OnboardingUrl.model_validate(resp.data)

    async def disconnect(self, agent_id: str, integration_id: str) -> None:
        await self._client.request(disconnect_bimpeai_integration_spec(agent_id, integration_id))


class _AsyncAgentCustomApiTools:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self, agent_id: str, integration_id: str) -> list[IntegrationTool]:
        resp = await self._client.request(list_custom_api_tools_spec(agent_id, integration_id))
        return [IntegrationTool.model_validate(item) for item in resp.data]

    async def add(
        self,
        agent_id: str,
        integration_id: str,
        body: CustomApiCreateToolBody,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> IntegrationTool:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(
            add_custom_api_tool_spec(agent_id, integration_id, dict(body), options)
        )
        return IntegrationTool.model_validate(resp.data)

    async def delete(self, agent_id: str, integration_id: str, tool_id: str) -> None:
        await self._client.request(delete_custom_api_tool_spec(agent_id, integration_id, tool_id))


class _AsyncAgentCustomApiIntegrations:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client
        self.tools = _AsyncAgentCustomApiTools(client)

    async def list(self, agent_id: str) -> list[CustomApiIntegration]:
        resp = await self._client.request(list_custom_api_integrations_spec(agent_id))
        return [CustomApiIntegration.model_validate(item) for item in resp.data]

    async def configure(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[CustomApiConfigureBody],
    ) -> CustomApiIntegration:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(
            configure_custom_api_integration_spec(agent_id, dict(body), options)
        )
        return CustomApiIntegration.model_validate(resp.data)

    async def disconnect(self, agent_id: str, integration_id: str) -> None:
        await self._client.request(disconnect_custom_api_integration_spec(agent_id, integration_id))


class _AsyncAgentMcpServerTools:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self, agent_id: str, integration_id: str) -> list[IntegrationTool]:
        resp = await self._client.request(list_mcp_server_tools_spec(agent_id, integration_id))
        return [IntegrationTool.model_validate(item) for item in resp.data]


class _AsyncAgentMcpServerIntegrations:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client
        self.tools = _AsyncAgentMcpServerTools(client)

    async def list(self, agent_id: str) -> list[McpServerIntegration]:
        resp = await self._client.request(list_mcp_server_integrations_spec(agent_id))
        return [McpServerIntegration.model_validate(item) for item in resp.data]

    async def configure(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[McpServerConfigureBody],
    ) -> McpServerIntegration:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(
            configure_mcp_server_integration_spec(agent_id, dict(body), options)
        )
        return McpServerIntegration.model_validate(resp.data)

    async def disconnect(self, agent_id: str, integration_id: str) -> None:
        await self._client.request(disconnect_mcp_server_integration_spec(agent_id, integration_id))

    async def discover(self, agent_id: str, integration_id: str) -> McpServerDiscoverResult:
        resp = await self._client.request(discover_mcp_server_tools_spec(agent_id, integration_id))
        return McpServerDiscoverResult.model_validate(resp.data)

    async def test(self, agent_id: str, integration_id: str) -> McpServerTestResult:
        resp = await self._client.request(test_mcp_server_connection_spec(agent_id, integration_id))
        return McpServerTestResult.model_validate(resp.data)


class _AsyncAgentPipedreamIntegrations:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self, agent_id: str) -> list[PipedreamIntegration]:
        resp = await self._client.request(list_pipedream_integrations_spec(agent_id))
        return [PipedreamIntegration.model_validate(item) for item in resp.data]

    async def configure(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[PipedreamConfigureBody],
    ) -> OnboardingUrl:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(
            configure_pipedream_integration_spec(agent_id, dict(body), options)
        )
        return OnboardingUrl.model_validate(resp.data)

    async def disconnect(self, agent_id: str, integration_id: str) -> None:
        await self._client.request(disconnect_pipedream_integration_spec(agent_id, integration_id))


class _AsyncAgentIntegrations:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client
        self.bimpeai = _AsyncAgentBimpeaiIntegrations(client)
        self.custom_api = _AsyncAgentCustomApiIntegrations(client)
        self.mcp_server = _AsyncAgentMcpServerIntegrations(client)
        self.pipedream = _AsyncAgentPipedreamIntegrations(client)

    async def list(self, agent_id: str) -> list[AgentIntegration]:
        items = await _alist_sub(self._client, agent_id, "integrations")
        return [AgentIntegration.model_validate(x) for x in items]


class _AsyncAgentChannels:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self, agent_id: str) -> list[AgentChannel]:
        items = await _alist_sub(self._client, agent_id, "channels")
        return [AgentChannel.model_validate(x) for x in items]


class _AsyncAgentActions:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self, agent_id: str) -> list[AgentAction]:
        items = await _alist_sub(self._client, agent_id, "actions")
        return [AgentAction.model_validate(x) for x in items]

    async def enable(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[BulkActionIdsBody],
    ) -> BulkActionUpdate:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(enable_actions_spec(agent_id, dict(body), options))
        return BulkActionUpdate.model_validate(resp.data)

    async def disable(
        self,
        agent_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[BulkActionIdsBody],
    ) -> BulkActionUpdate:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(disable_actions_spec(agent_id, dict(body), options))
        return BulkActionUpdate.model_validate(resp.data)


class _AsyncAgentKnowledgeBases:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self, agent_id: str) -> list[KnowledgeBaseItem]:
        items = await _alist_sub(self._client, agent_id, "knowledge_bases")
        return [KnowledgeBaseItem.model_validate(x) for x in items]

    async def create(
        self,
        agent_id: str,
        body: CreateKnowledgeBaseBody,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> KnowledgeBaseItem:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(create_knowledge_base_spec(agent_id, dict(body), options))
        return KnowledgeBaseItem.model_validate(resp.data)

    async def update(
        self, agent_id: str, kb_id: str, **body: Unpack[UpdateKnowledgeBaseBody]
    ) -> KnowledgeBaseItem:
        resp = await self._client.request(update_knowledge_base_spec(agent_id, kb_id, dict(body)))
        return KnowledgeBaseItem.model_validate(resp.data)

    async def delete(self, agent_id: str, kb_id: str) -> None:
        await self._client.request(delete_knowledge_base_spec(agent_id, kb_id))
