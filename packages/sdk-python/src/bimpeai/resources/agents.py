from __future__ import annotations

from typing import Any

from typing_extensions import Unpack

from .._request import RequestOptions
from ..pagination import AsyncPage, Page
from ..types.agents import (
    Agent,
    AgentAction,
    AgentCreateResponse,
    AgentDetail,
    BulkActionIdsBody,
    Channel,
    CreateAgentBody,
    CreateKnowledgeBaseBody,
    Integration,
    KnowledgeBase,
    UpdateAgentBody,
    UpdateKnowledgeBaseBody,
    UpdateLiveStatusBody,
)
from ._specs import (
    AsyncTransport,
    SyncTransport,
    bulk_agent_actions_spec,
    create_agent_spec,
    create_knowledge_base_spec,
    delete_knowledge_base_spec,
    list_agent_subresource_spec,
    list_agents_spec,
    retrieve_agent_spec,
    update_agent_live_status_spec,
    update_agent_spec,
    update_knowledge_base_spec,
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

    def update_live_status(self, agent_id: str, **body: Unpack[UpdateLiveStatusBody]) -> Agent:
        resp = self._client.request(update_agent_live_status_spec(agent_id, dict(body)))
        return Agent.model_validate(resp.data)


class _AgentIntegrations:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self, agent_id: str) -> list[Integration]:
        resp = self._client.request(list_agent_subresource_spec(agent_id, "integrations"))
        return [Integration.model_validate(item) for item in resp.data]


class _AgentChannels:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self, agent_id: str) -> list[Channel]:
        resp = self._client.request(list_agent_subresource_spec(agent_id, "channels"))
        return [Channel.model_validate(item) for item in resp.data]


class _AgentActions:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self, agent_id: str) -> list[AgentAction]:
        resp = self._client.request(list_agent_subresource_spec(agent_id, "actions"))
        return [AgentAction.model_validate(item) for item in resp.data]

    def enable(self, agent_id: str, body: BulkActionIdsBody) -> Any:
        resp = self._client.request(bulk_agent_actions_spec(agent_id, "enable", dict(body)))
        return resp.data

    def disable(self, agent_id: str, body: BulkActionIdsBody) -> Any:
        resp = self._client.request(bulk_agent_actions_spec(agent_id, "disable", dict(body)))
        return resp.data


class _AgentKnowledgeBases:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self, agent_id: str) -> list[KnowledgeBase]:
        resp = self._client.request(list_agent_subresource_spec(agent_id, "knowledge_bases"))
        return [KnowledgeBase.model_validate(item) for item in resp.data]

    def create(
        self,
        agent_id: str,
        body: CreateKnowledgeBaseBody,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> KnowledgeBase:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(create_knowledge_base_spec(agent_id, dict(body), options))
        return KnowledgeBase.model_validate(resp.data)

    def update(
        self, agent_id: str, kb_id: str, **body: Unpack[UpdateKnowledgeBaseBody]
    ) -> KnowledgeBase:
        resp = self._client.request(update_knowledge_base_spec(agent_id, kb_id, dict(body)))
        return KnowledgeBase.model_validate(resp.data)

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

    async def update_live_status(
        self, agent_id: str, **body: Unpack[UpdateLiveStatusBody]
    ) -> Agent:
        resp = await self._client.request(update_agent_live_status_spec(agent_id, dict(body)))
        return Agent.model_validate(resp.data)


async def _alist_sub(client: AsyncTransport, agent_id: str, name: str) -> list[Any]:
    resp = await client.request(list_agent_subresource_spec(agent_id, name))
    return list(resp.data)


class _AsyncAgentIntegrations:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self, agent_id: str) -> list[Integration]:
        items = await _alist_sub(self._client, agent_id, "integrations")
        return [Integration.model_validate(x) for x in items]


class _AsyncAgentChannels:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self, agent_id: str) -> list[Channel]:
        items = await _alist_sub(self._client, agent_id, "channels")
        return [Channel.model_validate(x) for x in items]


class _AsyncAgentActions:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self, agent_id: str) -> list[AgentAction]:
        items = await _alist_sub(self._client, agent_id, "actions")
        return [AgentAction.model_validate(x) for x in items]

    async def enable(self, agent_id: str, body: BulkActionIdsBody) -> Any:
        resp = await self._client.request(bulk_agent_actions_spec(agent_id, "enable", dict(body)))
        return resp.data

    async def disable(self, agent_id: str, body: BulkActionIdsBody) -> Any:
        resp = await self._client.request(bulk_agent_actions_spec(agent_id, "disable", dict(body)))
        return resp.data


class _AsyncAgentKnowledgeBases:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self, agent_id: str) -> list[KnowledgeBase]:
        items = await _alist_sub(self._client, agent_id, "knowledge_bases")
        return [KnowledgeBase.model_validate(x) for x in items]

    async def create(
        self,
        agent_id: str,
        body: CreateKnowledgeBaseBody,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> KnowledgeBase:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(create_knowledge_base_spec(agent_id, dict(body), options))
        return KnowledgeBase.model_validate(resp.data)

    async def update(
        self, agent_id: str, kb_id: str, **body: Unpack[UpdateKnowledgeBaseBody]
    ) -> KnowledgeBase:
        resp = await self._client.request(update_knowledge_base_spec(agent_id, kb_id, dict(body)))
        return KnowledgeBase.model_validate(resp.data)

    async def delete(self, agent_id: str, kb_id: str) -> None:
        await self._client.request(delete_knowledge_base_spec(agent_id, kb_id))
