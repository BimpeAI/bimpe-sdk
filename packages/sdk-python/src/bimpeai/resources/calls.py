from __future__ import annotations

from .._request import RequestOptions
from ..pagination import AsyncPage, Page
from ..types.calls import Call, CallDetail, CallStatus, MakeCallBody, MakeCallResult
from ._specs import (
    AsyncTransport,
    SyncTransport,
    list_calls_spec,
    make_call_spec,
    retrieve_call_spec,
)


class Calls:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(
        self,
        agent_id: str,
        *,
        page: int = 1,
        limit: int | None = None,
        search: str | None = None,
        sort: str | None = None,
        is_test_call: bool | None = None,
        status: CallStatus | None = None,
    ) -> Page[Call]:
        def fetch(current: int) -> Page[Call]:
            resp = self._client.request(
                list_calls_spec(
                    agent_id,
                    page=current,
                    limit=limit,
                    search=search,
                    sort=sort,
                    is_test_call=is_test_call,
                    status=status,
                )
            )
            data = [Call.model_validate(item) for item in resp.data]
            return Page(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return fetch(page)

    def make(
        self,
        agent_id: str,
        body: MakeCallBody,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> MakeCallResult:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(make_call_spec(agent_id, dict(body), options))
        return MakeCallResult.model_validate(resp.data)

    def retrieve(self, agent_id: str, call_id: str) -> CallDetail:
        resp = self._client.request(retrieve_call_spec(agent_id, call_id))
        return CallDetail.model_validate(resp.data)


class AsyncCalls:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(
        self,
        agent_id: str,
        *,
        page: int = 1,
        limit: int | None = None,
        search: str | None = None,
        sort: str | None = None,
        is_test_call: bool | None = None,
        status: CallStatus | None = None,
    ) -> AsyncPage[Call]:
        async def fetch(current: int) -> AsyncPage[Call]:
            resp = await self._client.request(
                list_calls_spec(
                    agent_id,
                    page=current,
                    limit=limit,
                    search=search,
                    sort=sort,
                    is_test_call=is_test_call,
                    status=status,
                )
            )
            data = [Call.model_validate(item) for item in resp.data]
            return AsyncPage(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return await fetch(page)

    async def make(
        self,
        agent_id: str,
        body: MakeCallBody,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> MakeCallResult:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(make_call_spec(agent_id, dict(body), options))
        return MakeCallResult.model_validate(resp.data)

    async def retrieve(self, agent_id: str, call_id: str) -> CallDetail:
        resp = await self._client.request(retrieve_call_spec(agent_id, call_id))
        return CallDetail.model_validate(resp.data)
