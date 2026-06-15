from __future__ import annotations

from .._request import RequestSpec
from ..types.calls import Call
from ._specs import AsyncTransport, SyncTransport


def _list_calls_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/calls")


class Calls:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self) -> list[Call]:
        resp = self._client.request(_list_calls_spec())
        return [Call.model_validate(item) for item in resp.data]


class AsyncCalls:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self) -> list[Call]:
        resp = await self._client.request(_list_calls_spec())
        return [Call.model_validate(item) for item in resp.data]
