import httpx
import pytest
import respx

from bimpeai import AsyncBimpeAI, AuthenticationError

BASE = "https://api.bimpeai.com/api/v1/console"


def agent(id_: str) -> dict[str, object]:
    return {"id": id_, "name": "Bot", "status": "active", "created_at": "t", "updated_at": "t"}


@respx.mock
async def test_async_list() -> None:
    respx.get(f"{BASE}/agents").mock(
        return_value=httpx.Response(
            200,
            json={
                "message": "ok",
                "data": [agent("a_1")],
                "meta": {
                    "total_count": 1,
                    "page_count": 1,
                    "current_page": 1,
                    "limit": 20,
                    "has_next_page": False,
                    "has_previous_page": False,
                },
            },
        )
    )
    async with AsyncBimpeAI(api_key="sk_test") as client:
        page = await client.agents.list()
        ids = [a.id async for a in page]
    assert ids == ["a_1"]


@respx.mock
async def test_async_auth_failure() -> None:
    respx.get(f"{BASE}/agents").mock(
        return_value=httpx.Response(401, json={"message": "no", "code": "api_key_missing"})
    )
    with pytest.raises(AuthenticationError):
        await AsyncBimpeAI(api_key="sk_test", max_retries=0).agents.list()
