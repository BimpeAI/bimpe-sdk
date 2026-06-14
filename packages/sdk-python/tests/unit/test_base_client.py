import httpx
import pytest

from bimpeai._base_client import BaseClient
from bimpeai._exceptions import NotFoundError, UserError


def client(
    *, base_url: str | None = None, default_headers: dict[str, str] | None = None
) -> BaseClient:
    return BaseClient(api_key="sk_test", base_url=base_url, default_headers=default_headers)


def test_requires_api_key() -> None:
    with pytest.raises(UserError):
        BaseClient(api_key="")


def test_build_url_and_params() -> None:
    c = client()
    assert c.build_url("/agents") == "https://api.bimpeai.com/api/v1/console/agents"
    assert c.clean_params({"page": 1, "search": None, "flag": True}) == {
        "page": "1",
        "flag": "true",
    }


def test_base_url_override_trims_slash() -> None:
    c = client(base_url="https://api.example.com/")
    assert c.build_url("/x") == "https://api.example.com/api/v1/console/x"


def test_build_headers_merge_and_override() -> None:
    c = client(default_headers={"X-Tenant": "t1"})
    headers = c.build_headers(
        has_body=True, idempotency_key="op-1", request_id="req-1", extra={"X-Tenant": "t2"}
    )
    assert headers["authorization"] == "Bearer sk_test"
    assert headers["content-type"] == "application/json"
    assert headers["idempotency-key"] == "op-1"
    assert headers["x-request-id"] == "req-1"
    assert headers["x-tenant"] == "t2"
    assert "bimpeai-python/" in headers["user-agent"]


def test_parse_response_raises_mapped_error() -> None:
    c = client()
    response = httpx.Response(
        404, json={"message": "missing"}, request=httpx.Request("GET", "https://x")
    )
    with pytest.raises(NotFoundError):
        c.parse_response(response, "req-1")


def test_parse_response_unwraps_and_backfills_request_id() -> None:
    c = client()
    response = httpx.Response(
        200,
        json={"message": "ok", "data": {"id": "a_1"}},
        request=httpx.Request("GET", "https://x"),
    )
    parsed = c.parse_response(response, "req-gen")
    assert parsed.data == {"id": "a_1"}
    assert parsed.request_id == "req-gen"
    assert parsed.status == 200
