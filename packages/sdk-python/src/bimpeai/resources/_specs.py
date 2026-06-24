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


def delete_agent_spec(agent_id: str) -> RequestSpec:
    return RequestSpec(method="DELETE", path=f"/agents/{agent_id}")


def update_live_status_spec(
    agent_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="PATCH", path=f"/agents/{agent_id}/live-status", body=dict(body), options=options
    )


def list_agent_subresource_spec(agent_id: str, name: str) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/agents/{agent_id}/{name}")


def get_test_code_spec(agent_id: str) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/agents/{agent_id}/deployment/agent-test-code")


def list_bimpeai_integrations_spec(agent_id: str) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/agents/{agent_id}/integrations/bimpeai")


def configure_bimpeai_integration_spec(
    agent_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path=f"/agents/{agent_id}/integrations/bimpeai/configure",
        body=dict(body),
        options=options,
    )


def disconnect_bimpeai_integration_spec(agent_id: str, integration_id: str) -> RequestSpec:
    return RequestSpec(
        method="DELETE", path=f"/agents/{agent_id}/integrations/bimpeai/{integration_id}"
    )


def list_custom_api_integrations_spec(agent_id: str) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/agents/{agent_id}/integrations/custom_api")


def configure_custom_api_integration_spec(
    agent_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path=f"/agents/{agent_id}/integrations/custom_api/configure",
        body=dict(body),
        options=options,
    )


def disconnect_custom_api_integration_spec(agent_id: str, integration_id: str) -> RequestSpec:
    return RequestSpec(
        method="DELETE", path=f"/agents/{agent_id}/integrations/custom_api/{integration_id}"
    )


def list_custom_api_tools_spec(agent_id: str, integration_id: str) -> RequestSpec:
    return RequestSpec(
        method="GET", path=f"/agents/{agent_id}/integrations/custom_api/{integration_id}/tools"
    )


def add_custom_api_tool_spec(
    agent_id: str, integration_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path=f"/agents/{agent_id}/integrations/custom_api/{integration_id}/tools",
        body=dict(body),
        options=options,
    )


def delete_custom_api_tool_spec(agent_id: str, integration_id: str, tool_id: str) -> RequestSpec:
    return RequestSpec(
        method="DELETE",
        path=f"/agents/{agent_id}/integrations/custom_api/{integration_id}/tools/{tool_id}",
    )


def list_mcp_server_integrations_spec(agent_id: str) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/agents/{agent_id}/integrations/mcp_server")


def configure_mcp_server_integration_spec(
    agent_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path=f"/agents/{agent_id}/integrations/mcp_server/configure",
        body=dict(body),
        options=options,
    )


def disconnect_mcp_server_integration_spec(agent_id: str, integration_id: str) -> RequestSpec:
    return RequestSpec(
        method="DELETE", path=f"/agents/{agent_id}/integrations/mcp_server/{integration_id}"
    )


def discover_mcp_server_tools_spec(agent_id: str, integration_id: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path=f"/agents/{agent_id}/integrations/mcp_server/{integration_id}/discover",
    )


def test_mcp_server_connection_spec(agent_id: str, integration_id: str) -> RequestSpec:
    return RequestSpec(
        method="POST", path=f"/agents/{agent_id}/integrations/mcp_server/{integration_id}/test"
    )


def list_mcp_server_tools_spec(agent_id: str, integration_id: str) -> RequestSpec:
    return RequestSpec(
        method="GET", path=f"/agents/{agent_id}/integrations/mcp_server/{integration_id}/tools"
    )


def list_pipedream_integrations_spec(agent_id: str) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/agents/{agent_id}/integrations/pipedream")


def configure_pipedream_integration_spec(
    agent_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path=f"/agents/{agent_id}/integrations/pipedream/configure",
        body=dict(body),
        options=options,
    )


def disconnect_pipedream_integration_spec(agent_id: str, integration_id: str) -> RequestSpec:
    return RequestSpec(
        method="DELETE", path=f"/agents/{agent_id}/integrations/pipedream/{integration_id}"
    )


def enable_actions_spec(
    agent_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="POST", path=f"/agents/{agent_id}/actions/enable", body=dict(body), options=options
    )


def disable_actions_spec(
    agent_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="POST", path=f"/agents/{agent_id}/actions/disable", body=dict(body), options=options
    )


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


def create_conversation_message_spec(
    agent_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path=f"/agents/{agent_id}/conversations/messages",
        body=dict(body),
        options=options,
    )


def set_ai_status_spec(
    agent_id: str, conversation_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="PATCH",
        path=f"/agents/{agent_id}/conversations/{conversation_id}/ai-status",
        body=dict(body),
        options=options,
    )


def retrieve_message_spec(agent_id: str, conversation_id: str, message_id: str) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path=f"/agents/{agent_id}/conversations/{conversation_id}/messages/{message_id}",
    )


def list_calls_spec(
    agent_id: str,
    *,
    page: int,
    limit: int | None,
    search: str | None,
    sort: str | None,
    is_test_call: bool | None,
    status: str | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path=f"/agents/{agent_id}/calls",
        query={
            "page": page,
            "limit": limit,
            "search": search,
            "sort": sort,
            "is_test_call": is_test_call,
            "status": status,
        },
    )


def make_call_spec(agent_id: str, body: dict[str, Any], options: RequestOptions) -> RequestSpec:
    return RequestSpec(
        method="POST", path=f"/agents/{agent_id}/calls", body=dict(body), options=options
    )


def retrieve_call_spec(agent_id: str, call_id: str) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/agents/{agent_id}/calls/{call_id}")


def clone_workflow_spec(body: dict[str, Any], options: RequestOptions) -> RequestSpec:
    return RequestSpec(method="POST", path="/workflows/clone", body=dict(body), options=options)


def list_phone_numbers_spec(
    *, page: int, limit: int | None, search: str | None, sort: str | None
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/phone-numbers",
        query={"page": page, "limit": limit, "search": search, "sort": sort},
    )


def retrieve_phone_number_spec(phone_number_id: str) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/phone-numbers/{phone_number_id}")


def update_phone_number_spec(
    phone_number_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="PATCH", path=f"/phone-numbers/{phone_number_id}", body=dict(body), options=options
    )


def list_phone_number_requests_spec(
    *, page: int, limit: int | None, search: str | None, sort: str | None
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/phone-numbers/request",
        query={"page": page, "limit": limit, "search": search, "sort": sort},
    )


def create_phone_number_request_spec(body: dict[str, Any], options: RequestOptions) -> RequestSpec:
    return RequestSpec(
        method="POST", path="/phone-numbers/request", body=dict(body), options=options
    )
