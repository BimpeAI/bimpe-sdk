from typing import Any

import httpx

from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec
from bimpeai.pagination import Page
from bimpeai.resources.phone_numbers import AsyncPhoneNumbers, PhoneNumbers
from bimpeai.types.phone_numbers import PhoneNumberDetail

NUMBER: dict[str, Any] = {
    "id": "pn_1",
    "agent_id": None,
    "label": None,
    "e164": "+15551234567",
}

DETAIL: dict[str, Any] = {
    **NUMBER,
    "agent_id": "a_1",
    "label": "Support line",
    "created_at": "now",
    "updated_at": "now",
    "inbound_enabled": True,
}


def response(data: Any) -> ApiResponse[Any]:
    return ApiResponse(data=data, meta=None, request_id="r", status=200, headers=httpx.Headers())


class FakeSync:
    def __init__(self, data: Any) -> None:
        self._data = data
        self.specs: list[RequestSpec] = []

    def request(self, spec: RequestSpec) -> ApiResponse[Any]:
        self.specs.append(spec)
        return response(self._data)


class FakeAsync:
    def __init__(self, data: Any) -> None:
        self._data = data
        self.specs: list[RequestSpec] = []

    async def request(self, spec: RequestSpec) -> ApiResponse[Any]:
        self.specs.append(spec)
        return response(self._data)


def test_list_builds_team_scoped_get_and_returns_page() -> None:
    client = FakeSync([NUMBER])
    page = PhoneNumbers(client).list(search="support")
    assert isinstance(page, Page)
    assert page.data[0].id == "pn_1"
    assert page.data[0].e164 == "+15551234567"
    spec = client.specs[-1]
    assert spec.method == "GET"
    assert spec.path == "/phone-numbers"
    assert spec.query == {"page": 1, "limit": None, "search": "support", "sort": None}


def test_retrieve_returns_detail_shape() -> None:
    client = FakeSync(DETAIL)
    out = PhoneNumbers(client).retrieve("pn_1")
    assert isinstance(out, PhoneNumberDetail)
    assert out.agent_id == "a_1"
    assert out.inbound_enabled is True
    assert client.specs[-1] == RequestSpec(method="GET", path="/phone-numbers/pn_1")


def test_update_patches_and_returns_detail() -> None:
    client = FakeSync({**DETAIL, "agent_id": "a_2", "label": "Sales"})
    out = PhoneNumbers(client).update("pn_1", agent_id="a_2", label="Sales", idempotency_key="op-1")
    assert isinstance(out, PhoneNumberDetail)
    assert out.agent_id == "a_2"
    spec = client.specs[-1]
    assert spec.method == "PATCH"
    assert spec.path == "/phone-numbers/pn_1"
    assert spec.body == {"agent_id": "a_2", "label": "Sales"}
    assert spec.options.idempotency_key == "op-1"


def test_requests_list_builds_get() -> None:
    client = FakeSync([NUMBER])
    page = PhoneNumbers(client).requests.list()
    assert isinstance(page, Page)
    assert page.data[0].id == "pn_1"
    spec = client.specs[-1]
    assert spec.method == "GET"
    assert spec.path == "/phone-numbers/request"
    assert spec.query == {"page": 1, "limit": None, "search": None, "sort": None}


def test_requests_create_posts_and_returns_none() -> None:
    client = FakeSync({"message": "ok"})
    out = PhoneNumbers(client).requests.create(
        business_name="Acme Support Ltd",
        intended_use="Inbound support",
        region="ng",
        agent_count=1,
        outbound_minutes=500,
        idempotency_key="op-2",
    )
    assert out is None
    spec = client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/phone-numbers/request"
    assert spec.body == {
        "business_name": "Acme Support Ltd",
        "intended_use": "Inbound support",
        "region": "ng",
        "agent_count": 1,
        "outbound_minutes": 500,
    }
    assert spec.options.idempotency_key == "op-2"


async def test_async_list_retrieve_and_request() -> None:
    list_client = FakeAsync([NUMBER])
    page = await AsyncPhoneNumbers(list_client).list()
    assert [n.id async for n in page] == ["pn_1"]
    assert list_client.specs[-1].path == "/phone-numbers"

    detail_client = FakeAsync(DETAIL)
    detail = await AsyncPhoneNumbers(detail_client).retrieve("pn_1")
    assert isinstance(detail, PhoneNumberDetail)
    assert detail.inbound_enabled is True

    req_client = FakeAsync({"message": "ok"})
    out = await AsyncPhoneNumbers(req_client).requests.create(
        business_name="Acme",
        intended_use="Support",
        region="uk",
        agent_count=2,
        outbound_minutes=0,
    )
    assert out is None
    spec = req_client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/phone-numbers/request"
    assert spec.body["region"] == "uk"
