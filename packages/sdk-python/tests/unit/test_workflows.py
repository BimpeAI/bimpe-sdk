from typing import Any

import httpx

from bimpeai._models import ApiResponse
from bimpeai._request import RequestSpec
from bimpeai.pagination import Page
from bimpeai.resources.workflows import AsyncWorkflows, Workflows
from bimpeai.types.workflows import Workflow


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


def _workflow(id_: str) -> dict[str, Any]:
    return {
        "id": id_,
        "name": "W",
        "description": None,
        "category": None,
        "visibility": "public",
        "is_owner": True,
        "system_prompt": "You triage support.",
        "rules": [],
        "flows": [],
        "tags": [],
        "created_at": "t",
        "updated_at": "t",
    }


def test_list_forwards_scope_and_returns_full_workflow() -> None:
    client = FakeSync([_workflow("w_1")])
    page = Workflows(client).list(scope="public")
    assert isinstance(page, Page)
    assert isinstance(page.data[0], Workflow)
    assert page.data[0].system_prompt == "You triage support."
    spec = client.specs[-1]
    assert spec.method == "GET"
    assert spec.path == "/workflows"
    assert spec.query == {
        "page": 1,
        "limit": None,
        "search": None,
        "sort": None,
        "scope": "public",
    }


def test_list_tolerates_server_placeholder_collections() -> None:
    # The live server returns setup_steps as a list of empty lists, and some
    # workflows carry empty-list placeholders inside flows/rules. None of that
    # may fail validation of the whole workflow.
    raw: dict[str, Any] = {
        **_workflow("w_3"),
        "setup_steps": [[], [], []],
        "flows": [{"name": "Menu Browsing", "category": "commerce"}, [], []],
        "rules": [
            {"id": "r1", "name": "R", "trigger": "t", "response": "resp", "enabled": True},
            [],
        ],
    }
    wf = Workflows(FakeSync([raw])).list(scope="public").data[0]
    assert isinstance(wf, Workflow)
    assert wf.setup_steps == [[], [], []]
    assert len(wf.flows) == 1 and wf.flows[0].name == "Menu Browsing"
    assert len(wf.rules) == 1 and wf.rules[0].id == "r1"


def test_list_tolerates_rule_missing_enabled() -> None:
    # A dict rule that omits enabled (and other fields) must parse rather than
    # fail validation of the whole workflow — only id is guaranteed on a Rule.
    raw: dict[str, Any] = {**_workflow("w_4"), "rules": [{"id": "r1", "name": "Partial"}]}
    wf = Workflows(FakeSync([raw])).list(scope="public").data[0]
    assert wf.rules[0].id == "r1"
    assert wf.rules[0].enabled is None
    assert wf.rules[0].response is None


def test_create_posts_body_and_returns_workflow() -> None:
    client = FakeSync(_workflow("w_1"))
    wf = Workflows(client).create(
        name="Triage", system_prompt="You triage support.", idempotency_key="op-1"
    )
    assert isinstance(wf, Workflow)
    assert wf.id == "w_1"
    spec = client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/workflows"
    assert spec.body == {"name": "Triage", "system_prompt": "You triage support."}
    assert spec.options.idempotency_key == "op-1"


def test_clone_posts_source_workflow_id() -> None:
    client = FakeSync({**_workflow("w_2"), "name": "Triage copy"})
    wf = Workflows(client).clone(source_workflow_id="w_1", idempotency_key="op-2")
    assert isinstance(wf, Workflow)
    assert wf.id == "w_2"
    spec = client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/workflows/clone"
    assert spec.body == {"source_workflow_id": "w_1"}
    assert spec.options.idempotency_key == "op-2"


def test_retrieve_update_delete_paths() -> None:
    client = FakeSync(_workflow("w_1"))
    wf = Workflows(client)

    retrieved = wf.retrieve("w_1")
    assert isinstance(retrieved, Workflow)
    assert client.specs[-1] == RequestSpec(method="GET", path="/workflows/w_1")

    updated = wf.update("w_1", tags=["v2"])
    assert isinstance(updated, Workflow)
    update_spec = client.specs[-1]
    assert update_spec.method == "PATCH"
    assert update_spec.path == "/workflows/w_1"
    assert update_spec.body == {"tags": ["v2"]}

    wf.delete("w_1")
    assert client.specs[-1] == RequestSpec(method="DELETE", path="/workflows/w_1")


async def test_async_list_and_clone() -> None:
    list_client = FakeAsync([_workflow("w_1")])
    page = await AsyncWorkflows(list_client).list()
    assert [w.id async for w in page] == ["w_1"]

    clone_client = FakeAsync({**_workflow("w_2"), "name": "Copy"})
    wf = await AsyncWorkflows(clone_client).clone(source_workflow_id="w_1")
    assert isinstance(wf, Workflow)
    assert wf.id == "w_2"
    spec = clone_client.specs[-1]
    assert spec.method == "POST"
    assert spec.path == "/workflows/clone"
    assert spec.body == {"source_workflow_id": "w_1"}
