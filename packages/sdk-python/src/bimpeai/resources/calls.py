from __future__ import annotations

from typing import Any

from .._request import RequestOptions, RequestSpec
from ..types.calls import Call, MakeCallBody, QueueCallBody
from ._specs import AsyncTransport, SyncTransport


def _list_calls_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/calls")


def _make_call_spec(body: MakeCallBody, options: RequestOptions) -> RequestSpec:
    return RequestSpec(method="POST", path="/calls", body=dict(body), options=options)


def _queue_call_spec(body: QueueCallBody, options: RequestOptions) -> RequestSpec:
    return RequestSpec(method="POST", path="/calls/queue", body=dict(body), options=options)


class Calls:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self) -> list[Call]:
        resp = self._client.request(_list_calls_spec())
        return [Call.model_validate(item) for item in resp.data]

    def make(
        self,
        body: MakeCallBody,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(_make_call_spec(body, options))
        return resp.data

    def queue(
        self,
        body: QueueCallBody,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(_queue_call_spec(body, options))
        return resp.data


class AsyncCalls:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self) -> list[Call]:
        resp = await self._client.request(_list_calls_spec())
        return [Call.model_validate(item) for item in resp.data]

    async def make(
        self,
        body: MakeCallBody,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(_make_call_spec(body, options))
        return resp.data

    async def queue(
        self,
        body: QueueCallBody,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(_queue_call_spec(body, options))
        return resp.data
