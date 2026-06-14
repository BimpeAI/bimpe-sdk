import pytest

import bimpeai
from bimpeai import AsyncBimpeAI, BimpeAI, UserError


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


def test_public_exports_present() -> None:
    for name in [
        "BimpeAI",
        "AsyncBimpeAI",
        "BimpeAIError",
        "APIError",
        "RateLimitError",
        "APINotImplementedError",
        "Page",
        "AsyncPage",
        "Agent",
        "Workflow",
        "Conversation",
        "Message",
        "StreamMessageEvent",
        "__version__",
    ]:
        assert hasattr(bimpeai, name)
