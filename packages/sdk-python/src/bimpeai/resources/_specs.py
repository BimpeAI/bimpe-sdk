from __future__ import annotations

from typing import Any, Protocol

from .._models import ApiResponse
from .._request import RequestOptions, RequestSpec


class SyncTransport(Protocol):
    def request(self, spec: RequestSpec) -> ApiResponse[Any]: ...


class AsyncTransport(Protocol):
    async def request(self, spec: RequestSpec) -> ApiResponse[Any]: ...


def list_agents_spec(
    *, page: int, limit: int | None, search: str | None, sort: str | None
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/agents",
        query={"page": page, "limit": limit, "search": search, "sort": sort},
    )


def create_agent_spec(body: dict[str, Any], options: RequestOptions) -> RequestSpec:
    return RequestSpec(method="POST", path="/agents", body=dict(body), options=options)


def retrieve_agent_spec(agent_id: str) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/agents/{agent_id}")


def update_agent_spec(agent_id: str, body: dict[str, Any]) -> RequestSpec:
    return RequestSpec(method="PATCH", path=f"/agents/{agent_id}", body=dict(body))


def list_agent_subresource_spec(agent_id: str, name: str) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/agents/{agent_id}/{name}")


def create_knowledge_base_spec(
    agent_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="POST", path=f"/agents/{agent_id}/knowledge_bases", body=dict(body), options=options
    )


def update_knowledge_base_spec(agent_id: str, kb_id: str, body: dict[str, Any]) -> RequestSpec:
    return RequestSpec(
        method="PATCH", path=f"/agents/{agent_id}/knowledge_bases/{kb_id}", body=dict(body)
    )


def delete_knowledge_base_spec(agent_id: str, kb_id: str) -> RequestSpec:
    return RequestSpec(method="DELETE", path=f"/agents/{agent_id}/knowledge_bases/{kb_id}")
