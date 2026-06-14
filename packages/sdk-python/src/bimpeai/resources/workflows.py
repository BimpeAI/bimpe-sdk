from __future__ import annotations

from typing import Any

from typing_extensions import Unpack

from .._request import RequestOptions, RequestSpec
from ..pagination import AsyncPage, Page
from ..types.workflows import (
    CreateWorkflowBody,
    UpdateWorkflowBody,
    Workflow,
    WorkflowScope,
    WorkflowSummary,
)
from ._specs import AsyncTransport, SyncTransport


def _list_spec(
    *,
    page: int,
    limit: int | None,
    search: str | None,
    sort: str | None,
    scope: WorkflowScope | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/workflows",
        query={"page": page, "limit": limit, "search": search, "sort": sort, "scope": scope},
    )


def _create_spec(body: dict[str, Any], options: RequestOptions) -> RequestSpec:
    return RequestSpec(method="POST", path="/workflows", body=dict(body), options=options)


def _retrieve_spec(workflow_id: str) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/workflows/{workflow_id}")


def _update_spec(workflow_id: str, body: dict[str, Any]) -> RequestSpec:
    return RequestSpec(method="PATCH", path=f"/workflows/{workflow_id}", body=dict(body))


def _delete_spec(workflow_id: str) -> RequestSpec:
    return RequestSpec(method="DELETE", path=f"/workflows/{workflow_id}")


class Workflows:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(
        self,
        *,
        page: int = 1,
        limit: int | None = None,
        search: str | None = None,
        sort: str | None = None,
        scope: WorkflowScope | None = None,
    ) -> Page[WorkflowSummary]:
        def fetch(current: int) -> Page[WorkflowSummary]:
            resp = self._client.request(
                _list_spec(page=current, limit=limit, search=search, sort=sort, scope=scope)
            )
            data = [WorkflowSummary.model_validate(item) for item in resp.data]
            return Page(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return fetch(page)

    def create(
        self,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[CreateWorkflowBody],
    ) -> Workflow:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(_create_spec(dict(body), options))
        return Workflow.model_validate(resp.data)

    def retrieve(self, workflow_id: str) -> Workflow:
        resp = self._client.request(_retrieve_spec(workflow_id))
        return Workflow.model_validate(resp.data)

    def update(self, workflow_id: str, **body: Unpack[UpdateWorkflowBody]) -> Workflow:
        resp = self._client.request(_update_spec(workflow_id, dict(body)))
        return Workflow.model_validate(resp.data)

    def delete(self, workflow_id: str) -> None:
        self._client.request(_delete_spec(workflow_id))


class AsyncWorkflows:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(
        self,
        *,
        page: int = 1,
        limit: int | None = None,
        search: str | None = None,
        sort: str | None = None,
        scope: WorkflowScope | None = None,
    ) -> AsyncPage[WorkflowSummary]:
        async def fetch(current: int) -> AsyncPage[WorkflowSummary]:
            resp = await self._client.request(
                _list_spec(page=current, limit=limit, search=search, sort=sort, scope=scope)
            )
            data = [WorkflowSummary.model_validate(item) for item in resp.data]
            return AsyncPage(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return await fetch(page)

    async def create(
        self,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[CreateWorkflowBody],
    ) -> Workflow:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(_create_spec(dict(body), options))
        return Workflow.model_validate(resp.data)

    async def retrieve(self, workflow_id: str) -> Workflow:
        resp = await self._client.request(_retrieve_spec(workflow_id))
        return Workflow.model_validate(resp.data)

    async def update(self, workflow_id: str, **body: Unpack[UpdateWorkflowBody]) -> Workflow:
        resp = await self._client.request(_update_spec(workflow_id, dict(body)))
        return Workflow.model_validate(resp.data)

    async def delete(self, workflow_id: str) -> None:
        await self._client.request(_delete_spec(workflow_id))
