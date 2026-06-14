import json

import httpx
import pytest
import respx

from bimpeai._client import BimpeAI
from bimpeai._exceptions import APITimeoutError, AuthenticationError, RateLimitError
from bimpeai._request import RequestOptions, RequestSpec, StreamSpec

BASE = "https://api.bimpeai.com/api/v1/console"


def make() -> BimpeAI:
    return BimpeAI(api_key="sk_test")


@respx.mock
def test_get_sends_auth_user_agent_and_request_id() -> None:
    route = respx.get(f"{BASE}/agents").mock(
        return_value=httpx.Response(200, json={"message": "ok", "data": []})
    )
    make().request(RequestSpec(method="GET", path="/agents", query={"page": 1}))
    req = route.calls.last.request
    assert req.url.params["page"] == "1"
    assert req.headers["authorization"] == "Bearer sk_test"
    assert req.headers["user-agent"].startswith("bimpeai-python/")
    assert len(req.headers["x-request-id"]) == 36


@respx.mock
def test_post_sends_json_body() -> None:
    route = respx.post(f"{BASE}/agents").mock(
        return_value=httpx.Response(201, json={"message": "ok", "data": {"id": "a_1"}})
    )
    make().request(RequestSpec(method="POST", path="/agents", body={"name": "A"}))
    request = route.calls.last.request
    assert request.headers["content-type"] == "application/json"
    assert json.loads(request.content) == {"name": "A"}


@respx.mock
def test_maps_401() -> None:
    respx.get(f"{BASE}/agents").mock(
        return_value=httpx.Response(401, json={"message": "no key", "code": "api_key_missing"})
    )
    with pytest.raises(AuthenticationError):
        BimpeAI(api_key="sk_test", max_retries=0).request(RequestSpec(method="GET", path="/agents"))


@respx.mock
def test_retries_500_then_succeeds() -> None:
    route = respx.get(f"{BASE}/agents").mock(
        side_effect=[
            httpx.Response(500, json={"message": "oops"}),
            httpx.Response(200, json={"message": "ok", "data": []}),
        ]
    )
    make().request(RequestSpec(method="GET", path="/agents"))
    assert route.call_count == 2


@respx.mock
def test_idempotency_key_constant_across_retries() -> None:
    keys: list[str] = []
    responses = [
        httpx.Response(500, json={"message": "oops"}),
        httpx.Response(201, json={"message": "ok", "data": {"id": "a_1"}}),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        keys.append(request.headers["idempotency-key"])
        return responses[len(keys) - 1]

    respx.post(f"{BASE}/agents").mock(side_effect=handler)
    make().request(RequestSpec(method="POST", path="/agents", body={"name": "A"}))
    assert len(keys) == 2
    assert keys[0] == keys[1]
    assert len(keys[0]) == 36


@respx.mock
def test_idempotency_autogen_only_when_retries_on() -> None:
    respx.post(f"{BASE}/agents").mock(
        return_value=httpx.Response(201, json={"message": "ok", "data": {"id": "a_1"}})
    )
    calls = respx.calls
    BimpeAI(api_key="sk_test", max_retries=2).request(
        RequestSpec(method="POST", path="/agents", body={"name": "A"})
    )
    assert "idempotency-key" in calls.last.request.headers
    BimpeAI(api_key="sk_test", max_retries=0).request(
        RequestSpec(method="POST", path="/agents", body={"name": "A"})
    )
    assert "idempotency-key" not in calls.last.request.headers


@respx.mock
def test_no_idempotency_on_get() -> None:
    route = respx.get(f"{BASE}/agents").mock(
        return_value=httpx.Response(200, json={"message": "ok", "data": []})
    )
    make().request(RequestSpec(method="GET", path="/agents"))
    assert "idempotency-key" not in route.calls.last.request.headers


@respx.mock
def test_timeout_maps_to_api_timeout() -> None:
    respx.get(f"{BASE}/agents").mock(side_effect=httpx.TimeoutException("t"))
    with pytest.raises(APITimeoutError):
        BimpeAI(api_key="sk_test", max_retries=0).request(RequestSpec(method="GET", path="/agents"))


@respx.mock
def test_stream_open_sets_event_stream_and_omits_auth() -> None:
    route = respx.get(f"{BASE}/agents/a_1/conversations/c_1/messages/stream").mock(
        return_value=httpx.Response(
            200, content=b"data: x\n\n", headers={"content-type": "text/event-stream"}
        )
    )
    with make().stream(
        StreamSpec(path="/agents/a_1/conversations/c_1/messages/stream", query={"ticket": "t1"})
    ) as response:
        list(response.iter_bytes())
    req = route.calls.last.request
    assert req.headers["accept"] == "text/event-stream"
    assert "authorization" not in req.headers
    assert req.url.params["ticket"] == "t1"


@respx.mock
def test_stream_open_maps_rate_limit() -> None:
    respx.get(f"{BASE}/x").mock(
        return_value=httpx.Response(429, json={"message": "too many", "code": "too_many_requests"})
    )
    with pytest.raises(RateLimitError), make().stream(StreamSpec(path="/x")) as _response:
        pass


def test_unused_options_import() -> None:
    assert RequestOptions().idempotency_key is None
