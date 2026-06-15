import httpx
import respx

from bimpeai import AsyncBimpeAI, BimpeAI

BASE = "https://api.bimpe.ai/api/v1/console"
TICKET = f"{BASE}/agents/a_1/conversations/c_1/stream-ticket"
STREAM = f"{BASE}/agents/a_1/conversations/c_1/messages/stream"

EVENTS = (
    b'id: m_1\nevent: message\ndata: {"id":"m_1","conversation_id":"c_1","role":"user","message":"hi","message_type":"text","created_at":"t"}\n\n'  # noqa: E501
    b'event: heartbeat\ndata: {"ts":1}\n\n'
    b'id: m_2\nevent: message\ndata: {"id":"m_2","conversation_id":"c_1","role":"assistant","message":"yo","message_type":"text","created_at":"t"}\n\n'  # noqa: E501
)


@respx.mock
def test_sync_stream_end_to_end() -> None:
    respx.post(TICKET).mock(
        return_value=httpx.Response(
            201, json={"message": "ok", "data": {"ticket": "t1", "expires_in": 60}}
        )
    )
    respx.get(STREAM).mock(
        return_value=httpx.Response(
            200, content=EVENTS, headers={"content-type": "text/event-stream"}
        )
    )
    ids = [
        event.id
        for event in BimpeAI(api_key="sk_test").conversations.messages.stream(
            "a_1", "c_1", reconnect=False
        )
    ]
    assert ids == ["m_1", "m_2"]


@respx.mock
async def test_async_stream_end_to_end() -> None:
    respx.post(TICKET).mock(
        return_value=httpx.Response(
            201, json={"message": "ok", "data": {"ticket": "t1", "expires_in": 60}}
        )
    )
    respx.get(STREAM).mock(
        return_value=httpx.Response(
            200, content=EVENTS, headers={"content-type": "text/event-stream"}
        )
    )
    async with AsyncBimpeAI(api_key="sk_test") as client:
        ids = [
            event.id
            async for event in client.conversations.messages.stream("a_1", "c_1", reconnect=False)
        ]
    assert ids == ["m_1", "m_2"]
