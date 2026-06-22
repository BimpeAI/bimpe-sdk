import pytest

import bimpeai
from bimpeai import AsyncBimpeAI, BimpeAI, UserError

EXPECTED_ALL = [
    "Agent",
    "AgentAction",
    "AgentChannel",
    "AgentCreateResponse",
    "AgentDetail",
    "AgentIntegration",
    "AgentLiveStatus",
    "APIConnectionError",
    "APIError",
    "APINotImplementedError",
    "APITimeoutError",
    "ApiResponse",
    "AsyncBimpeAI",
    "AsyncPage",
    "AuthenticationError",
    "BadRequestError",
    "BimpeAI",
    "BimpeAIError",
    "BulkActionUpdate",
    "Call",
    "CallDetail",
    "ConflictError",
    "Conversation",
    "ConversationDetail",
    "ErrorCode",
    "IntegrationSummary",
    "InternalServerError",
    "KnowledgeBaseItem",
    "KnowledgeBaseSummary",
    "MakeCallResult",
    "Message",
    "NotFoundError",
    "Page",
    "PaginationMeta",
    "PermissionDeniedError",
    "RateLimitError",
    "Rule",
    "StreamHeartbeatEvent",
    "StreamMessageEvent",
    "StreamTicket",
    "UserError",
    "ValidationError",
    "Workflow",
    "WorkflowDetail",
    "WorkflowSummary",
    "__version__",
]


def test_sync_client_exposes_resources() -> None:
    client = BimpeAI(api_key="sk_test")
    assert client.agents is not None
    assert client.workflows is not None
    assert client.conversations is not None
    assert client.conversations.messages is not None
    assert client.calls is not None
    client.close()


async def test_async_client_exposes_resources() -> None:
    client = AsyncBimpeAI(api_key="sk_test")
    assert client.agents is not None
    assert client.conversations.messages is not None
    await client.aclose()


def test_user_error_on_empty_key() -> None:
    with pytest.raises(UserError):
        BimpeAI(api_key="")


def test_all_matches_expected_exactly() -> None:
    assert bimpeai.__all__ == EXPECTED_ALL


def test_all_names_are_importable() -> None:
    for name in bimpeai.__all__:
        assert hasattr(bimpeai, name), name
