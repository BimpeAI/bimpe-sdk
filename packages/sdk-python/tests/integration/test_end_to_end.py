import json

import httpx
import pytest
import respx

from bimpeai import AuthenticationError, BimpeAI, RateLimitError

BASE = "https://api.bimpe.ai/api/v1/console"


def meta(current: int, has_next: bool) -> dict[str, object]:
    return {
        "total_count": 5,
        "page_count": 3,
        "current_page": current,
        "limit": 2,
        "has_next_page": has_next,
        "has_previous_page": current > 1,
    }


def agent(id_: str) -> dict[str, object]:
    return {
        "id": id_,
        "name": "Bot",
        "description": "Support",
        "workflow_id": "w_1",
        "status": "development",
        "created_at": "t",
        "updated_at": "t",
    }


@respx.mock
def test_auth_and_list() -> None:
    respx.get(f"{BASE}/agents").mock(
        return_value=httpx.Response(
            200, json={"message": "ok", "data": [agent("a_1")], "meta": meta(1, False)}
        )
    )
    with BimpeAI(api_key="sk_test") as client:
        page = client.agents.list()
    assert [a.id for a in page] == ["a_1"]


@respx.mock
def test_auth_failure() -> None:
    respx.get(f"{BASE}/agents").mock(
        return_value=httpx.Response(401, json={"message": "no", "code": "api_key_missing"})
    )
    with pytest.raises(AuthenticationError):
        BimpeAI(api_key="sk_test", max_retries=0).agents.list()


@respx.mock
def test_retry_then_success() -> None:
    route = respx.get(f"{BASE}/agents").mock(
        side_effect=[
            httpx.Response(500, json={"message": "oops"}),
            httpx.Response(
                200, json={"message": "ok", "data": [agent("a_1")], "meta": meta(1, False)}
            ),
        ]
    )
    BimpeAI(api_key="sk_test").agents.list()
    assert route.call_count == 2


@respx.mock
def test_rate_limited_surfaces_metadata() -> None:
    respx.get(f"{BASE}/agents").mock(
        return_value=httpx.Response(
            429, json={"message": "slow"}, headers={"retry-after": "3", "x-ratelimit-limit": "30"}
        )
    )
    try:
        BimpeAI(api_key="sk_test", max_retries=0).agents.list()
    except RateLimitError as err:
        assert err.retry_after == 3
        assert err.limit == 30
    else:
        raise AssertionError("expected RateLimitError")


@respx.mock
def test_pagination_across_pages() -> None:
    pages = {
        "1": {"data": [agent("a_1"), agent("a_2")], "meta": meta(1, True)},
        "2": {"data": [agent("a_3")], "meta": meta(2, False)},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        page = request.url.params.get("page", "1")
        body = pages[page]
        return httpx.Response(200, json={"message": "ok", **body})

    respx.get(f"{BASE}/agents").mock(side_effect=handler)
    ids = [a.id for a in BimpeAI(api_key="sk_test").agents.list(limit=2)]
    assert ids == ["a_1", "a_2", "a_3"]


@respx.mock
def test_send_message() -> None:
    route = respx.post(f"{BASE}/agents/a_1/conversations/c_1/messages").mock(
        return_value=httpx.Response(
            201,
            json={
                "message": "ok",
                "data": {
                    "id": "m_1",
                    "role": "assistant",
                    "message": "hi",
                    "message_type": "text",
                    "created_at": "t",
                },
            },
        )
    )
    sent = BimpeAI(api_key="sk_test").conversations.messages.send("a_1", "c_1", message="Hi")
    assert sent.id == "m_1"
    assert json.loads(route.calls.last.request.content) == {"message": "Hi"}
