import json

import httpx
import pytest
import respx

from bimpeai._async_client import AsyncBimpeAI
from bimpeai._exceptions import APITimeoutError, AuthenticationError, RateLimitError
from bimpeai._request import RequestSpec, StreamSpec

BASE = "https://api.bimpeai.com/api/v1/console"


def make() -> AsyncBimpeAI:
    return AsyncBimpeAI(api_key="sk_test")


@respx.mock
async def test_get_sends_auth_and_request_id() -> None:
    route = respx.get(f"{BASE}/agents").mock(
        return_value=httpx.Response(200, json={"message": "ok", "data": []})
    )
    await make().request(RequestSpec(method="GET", path="/agents", query={"page": 1}))
    req = route.calls.last.request
    assert req.url.params["page"] == "1"
    assert req.headers["authorization"] == "Bearer sk_test"
    assert len(req.headers["x-request-id"]) == 36


@respx.mock
async def test_post_sends_json_body() -> None:
    route = respx.post(f"{BASE}/agents").mock(
        return_value=httpx.Response(201, json={"message": "ok", "data": {"id": "a_1"}})
    )
    await make().request(RequestSpec(method="POST", path="/agents", body={"name": "A"}))
    request = route.calls.last.request
    assert request.headers["content-type"] == "application/json"
    assert json.loads(request.content) == {"name": "A"}


@respx.mock
async def test_maps_401() -> None:
    respx.get(f"{BASE}/agents").mock(
        return_value=httpx.Response(401, json={"message": "no key", "code": "api_key_missing"})
    )
    with pytest.raises(AuthenticationError):
        await AsyncBimpeAI(api_key="sk_test", max_retries=0).request(
            RequestSpec(method="GET", path="/agents")
        )


@respx.mock
async def test_retries_500_then_succeeds() -> None:
    route = respx.get(f"{BASE}/agents").mock(
        side_effect=[
            httpx.Response(500, json={"message": "oops"}),
            httpx.Response(200, json={"message": "ok", "data": []}),
        ]
    )
    await make().request(RequestSpec(method="GET", path="/agents"))
    assert route.call_count == 2


@respx.mock
async def test_idempotency_key_constant_across_retries() -> None:
    keys: list[str] = []
    responses = [
        httpx.Response(500, json={"message": "oops"}),
        httpx.Response(201, json={"message": "ok", "data": {"id": "a_1"}}),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        keys.append(request.headers["idempotency-key"])
        return responses[len(keys) - 1]

    respx.post(f"{BASE}/agents").mock(side_effect=handler)
    await make().request(RequestSpec(method="POST", path="/agents", body={"name": "A"}))
    assert len(keys) == 2
    assert keys[0] == keys[1]


@respx.mock
async def test_timeout_maps_to_api_timeout() -> None:
    respx.get(f"{BASE}/agents").mock(side_effect=httpx.TimeoutException("t"))
    with pytest.raises(APITimeoutError):
        await AsyncBimpeAI(api_key="sk_test", max_retries=0).request(
            RequestSpec(method="GET", path="/agents")
        )


@respx.mock
async def test_stream_open_sets_event_stream_and_omits_auth() -> None:
    route = respx.get(f"{BASE}/x").mock(
        return_value=httpx.Response(
            200, content=b"data: x\n\n", headers={"content-type": "text/event-stream"}
        )
    )
    async with make().stream(StreamSpec(path="/x", query={"ticket": "t1"})) as response:
        async for _chunk in response.aiter_bytes():
            pass
    req = route.calls.last.request
    assert req.headers["accept"] == "text/event-stream"
    assert "authorization" not in req.headers
    assert req.url.params["ticket"] == "t1"


@respx.mock
async def test_stream_open_maps_rate_limit() -> None:
    respx.get(f"{BASE}/x").mock(
        return_value=httpx.Response(429, json={"message": "too many", "code": "too_many_requests"})
    )
    with pytest.raises(RateLimitError):
        async with make().stream(StreamSpec(path="/x")) as _response:
            pass
