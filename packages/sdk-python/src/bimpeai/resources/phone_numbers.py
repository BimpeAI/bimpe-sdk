from __future__ import annotations

from typing_extensions import Unpack

from .._request import RequestOptions
from ..pagination import AsyncPage, Page
from ..types.phone_numbers import (
    CreatePhoneNumberRequestBody,
    PhoneNumber,
    PhoneNumberDetail,
    UpdatePhoneNumberBody,
)
from ._specs import (
    AsyncTransport,
    SyncTransport,
    create_phone_number_request_spec,
    list_phone_number_requests_spec,
    list_phone_numbers_spec,
    retrieve_phone_number_spec,
    update_phone_number_spec,
)


class PhoneNumbers:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client
        self.requests = _PhoneNumberRequests(client)

    def list(
        self,
        *,
        page: int = 1,
        limit: int | None = None,
        search: str | None = None,
        sort: str | None = None,
    ) -> Page[PhoneNumber]:
        def fetch(current: int) -> Page[PhoneNumber]:
            resp = self._client.request(
                list_phone_numbers_spec(page=current, limit=limit, search=search, sort=sort)
            )
            data = [PhoneNumber.model_validate(item) for item in resp.data]
            return Page(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return fetch(page)

    def retrieve(self, phone_number_id: str) -> PhoneNumberDetail:
        resp = self._client.request(retrieve_phone_number_spec(phone_number_id))
        return PhoneNumberDetail.model_validate(resp.data)

    def update(
        self,
        phone_number_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[UpdatePhoneNumberBody],
    ) -> PhoneNumberDetail:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(update_phone_number_spec(phone_number_id, dict(body), options))
        return PhoneNumberDetail.model_validate(resp.data)


class _PhoneNumberRequests:
    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(
        self,
        *,
        page: int = 1,
        limit: int | None = None,
        search: str | None = None,
        sort: str | None = None,
    ) -> Page[PhoneNumber]:
        def fetch(current: int) -> Page[PhoneNumber]:
            resp = self._client.request(
                list_phone_number_requests_spec(page=current, limit=limit, search=search, sort=sort)
            )
            data = [PhoneNumber.model_validate(item) for item in resp.data]
            return Page(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return fetch(page)

    def create(
        self,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[CreatePhoneNumberRequestBody],
    ) -> None:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        self._client.request(create_phone_number_request_spec(dict(body), options))


class AsyncPhoneNumbers:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client
        self.requests = _AsyncPhoneNumberRequests(client)

    async def list(
        self,
        *,
        page: int = 1,
        limit: int | None = None,
        search: str | None = None,
        sort: str | None = None,
    ) -> AsyncPage[PhoneNumber]:
        async def fetch(current: int) -> AsyncPage[PhoneNumber]:
            resp = await self._client.request(
                list_phone_numbers_spec(page=current, limit=limit, search=search, sort=sort)
            )
            data = [PhoneNumber.model_validate(item) for item in resp.data]
            return AsyncPage(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return await fetch(page)

    async def retrieve(self, phone_number_id: str) -> PhoneNumberDetail:
        resp = await self._client.request(retrieve_phone_number_spec(phone_number_id))
        return PhoneNumberDetail.model_validate(resp.data)

    async def update(
        self,
        phone_number_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[UpdatePhoneNumberBody],
    ) -> PhoneNumberDetail:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(
            update_phone_number_spec(phone_number_id, dict(body), options)
        )
        return PhoneNumberDetail.model_validate(resp.data)


class _AsyncPhoneNumberRequests:
    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(
        self,
        *,
        page: int = 1,
        limit: int | None = None,
        search: str | None = None,
        sort: str | None = None,
    ) -> AsyncPage[PhoneNumber]:
        async def fetch(current: int) -> AsyncPage[PhoneNumber]:
            resp = await self._client.request(
                list_phone_number_requests_spec(page=current, limit=limit, search=search, sort=sort)
            )
            data = [PhoneNumber.model_validate(item) for item in resp.data]
            return AsyncPage(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return await fetch(page)

    async def create(
        self,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[CreatePhoneNumberRequestBody],
    ) -> None:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        await self._client.request(create_phone_number_request_spec(dict(body), options))
