from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Iterator
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, Protocol

import httpx
from pydantic import ValidationError as PydanticValidationError
from typing_extensions import Unpack

from .._exceptions import BimpeAIError
from .._models import ApiResponse
from .._request import RequestOptions, RequestSpec, StreamSpec
from .._retries import compute_backoff, should_retry
from .._sse import aparse_sse, parse_sse
from ..pagination import AsyncPage, Page
from ..types.conversations import (
    Conversation,
    ConversationChannel,
    Message,
    SendMessageBody,
    StreamMessageEvent,
    StreamTicket,
)

_DEFAULT_STREAM_RETRIES = 5


class SyncStreamTransport(Protocol):
    def request(self, spec: RequestSpec) -> ApiResponse[Any]: ...
    def stream(self, spec: StreamSpec) -> AbstractContextManager[httpx.Response]: ...


class AsyncStreamTransport(Protocol):
    async def request(self, spec: RequestSpec) -> ApiResponse[Any]: ...
    def stream(self, spec: StreamSpec) -> AbstractAsyncContextManager[httpx.Response]: ...


def _list_conversations_spec(
    agent_id: str,
    *,
    page: int,
    limit: int | None,
    search: str | None,
    channel: ConversationChannel | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path=f"/agents/{agent_id}/conversations",
        query={"page": page, "limit": limit, "search": search, "channel": channel},
    )


def _retrieve_conversation_spec(agent_id: str, conversation_id: str) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/agents/{agent_id}/conversations/{conversation_id}")


def _list_messages_spec(
    agent_id: str, conversation_id: str, *, page: int, limit: int | None
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path=f"/agents/{agent_id}/conversations/{conversation_id}/messages",
        query={"page": page, "limit": limit},
    )


def _send_message_spec(
    agent_id: str, conversation_id: str, body: dict[str, Any], options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path=f"/agents/{agent_id}/conversations/{conversation_id}/messages",
        body=dict(body),
        options=options,
    )


def _stream_ticket_spec(
    agent_id: str, conversation_id: str, options: RequestOptions
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path=f"/agents/{agent_id}/conversations/{conversation_id}/stream-ticket",
        options=options,
    )


def _stream_path(agent_id: str, conversation_id: str) -> str:
    return f"/agents/{agent_id}/conversations/{conversation_id}/messages/stream"


def _parse_stream_message(data: str) -> StreamMessageEvent | None:
    try:
        return StreamMessageEvent.model_validate_json(data)
    except PydanticValidationError:
        return None


class Messages:
    def __init__(self, client: SyncStreamTransport) -> None:
        self._client = client

    def list(
        self, agent_id: str, conversation_id: str, *, page: int = 1, limit: int | None = None
    ) -> Page[Message]:
        def fetch(current: int) -> Page[Message]:
            resp = self._client.request(
                _list_messages_spec(agent_id, conversation_id, page=current, limit=limit)
            )
            data = [Message.model_validate(item) for item in resp.data]
            return Page(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return fetch(page)

    def send(
        self,
        agent_id: str,
        conversation_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[SendMessageBody],
    ) -> Message:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(
            _send_message_spec(agent_id, conversation_id, dict(body), options)
        )
        return Message.model_validate(resp.data)

    def stream_ticket(
        self,
        agent_id: str,
        conversation_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> StreamTicket:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = self._client.request(_stream_ticket_spec(agent_id, conversation_id, options))
        return StreamTicket.model_validate(resp.data)

    def stream(
        self,
        agent_id: str,
        conversation_id: str,
        *,
        after: str | None = None,
        reconnect: bool = True,
        max_retries: int = _DEFAULT_STREAM_RETRIES,
        timeout: float | None = None,
    ) -> Iterator[StreamMessageEvent]:
        current_after = after
        attempt = 0
        path = _stream_path(agent_id, conversation_id)
        while True:
            try:
                ticket = self.stream_ticket(agent_id, conversation_id).ticket
                query: dict[str, Any] = {"ticket": ticket}
                if current_after is not None:
                    query["after"] = current_after
                with self._client.stream(
                    StreamSpec(path=path, query=query, timeout=timeout)
                ) as response:
                    for event in parse_sse(response.iter_bytes()):
                        if event.event != "message":
                            continue
                        message = _parse_stream_message(event.data)
                        if message is None:
                            continue
                        if event.id:
                            current_after = event.id
                        attempt = 0
                        yield message
            except BimpeAIError as error:
                if not reconnect or not should_retry(error, attempt, max_retries):
                    raise
                time.sleep(compute_backoff(attempt))
                attempt += 1
                continue
            if not reconnect or attempt >= max_retries:
                return
            time.sleep(compute_backoff(attempt))
            attempt += 1


class Conversations:
    def __init__(self, client: SyncStreamTransport) -> None:
        self._client = client
        self.messages = Messages(client)

    def list(
        self,
        agent_id: str,
        *,
        page: int = 1,
        limit: int | None = None,
        search: str | None = None,
        channel: ConversationChannel | None = None,
    ) -> Page[Conversation]:
        def fetch(current: int) -> Page[Conversation]:
            resp = self._client.request(
                _list_conversations_spec(
                    agent_id, page=current, limit=limit, search=search, channel=channel
                )
            )
            data = [Conversation.model_validate(item) for item in resp.data]
            return Page(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return fetch(page)

    def retrieve(self, agent_id: str, conversation_id: str) -> Conversation:
        resp = self._client.request(_retrieve_conversation_spec(agent_id, conversation_id))
        return Conversation.model_validate(resp.data)


class AsyncMessages:
    def __init__(self, client: AsyncStreamTransport) -> None:
        self._client = client

    async def list(
        self, agent_id: str, conversation_id: str, *, page: int = 1, limit: int | None = None
    ) -> AsyncPage[Message]:
        async def fetch(current: int) -> AsyncPage[Message]:
            resp = await self._client.request(
                _list_messages_spec(agent_id, conversation_id, page=current, limit=limit)
            )
            data = [Message.model_validate(item) for item in resp.data]
            return AsyncPage(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return await fetch(page)

    async def send(
        self,
        agent_id: str,
        conversation_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        **body: Unpack[SendMessageBody],
    ) -> Message:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(
            _send_message_spec(agent_id, conversation_id, dict(body), options)
        )
        return Message.model_validate(resp.data)

    async def stream_ticket(
        self,
        agent_id: str,
        conversation_id: str,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> StreamTicket:
        options = RequestOptions(
            idempotency_key=idempotency_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        resp = await self._client.request(_stream_ticket_spec(agent_id, conversation_id, options))
        return StreamTicket.model_validate(resp.data)

    async def stream(
        self,
        agent_id: str,
        conversation_id: str,
        *,
        after: str | None = None,
        reconnect: bool = True,
        max_retries: int = _DEFAULT_STREAM_RETRIES,
        timeout: float | None = None,
    ) -> AsyncIterator[StreamMessageEvent]:
        current_after = after
        attempt = 0
        path = _stream_path(agent_id, conversation_id)
        while True:
            try:
                ticket = (await self.stream_ticket(agent_id, conversation_id)).ticket
                query: dict[str, Any] = {"ticket": ticket}
                if current_after is not None:
                    query["after"] = current_after
                async with self._client.stream(
                    StreamSpec(path=path, query=query, timeout=timeout)
                ) as response:
                    async for event in aparse_sse(response.aiter_bytes()):
                        if event.event != "message":
                            continue
                        message = _parse_stream_message(event.data)
                        if message is None:
                            continue
                        if event.id:
                            current_after = event.id
                        attempt = 0
                        yield message
            except BimpeAIError as error:
                if not reconnect or not should_retry(error, attempt, max_retries):
                    raise
                await asyncio.sleep(compute_backoff(attempt))
                attempt += 1
                continue
            if not reconnect or attempt >= max_retries:
                return
            await asyncio.sleep(compute_backoff(attempt))
            attempt += 1


class AsyncConversations:
    def __init__(self, client: AsyncStreamTransport) -> None:
        self._client = client
        self.messages = AsyncMessages(client)

    async def list(
        self,
        agent_id: str,
        *,
        page: int = 1,
        limit: int | None = None,
        search: str | None = None,
        channel: ConversationChannel | None = None,
    ) -> AsyncPage[Conversation]:
        async def fetch(current: int) -> AsyncPage[Conversation]:
            resp = await self._client.request(
                _list_conversations_spec(
                    agent_id, page=current, limit=limit, search=search, channel=channel
                )
            )
            data = [Conversation.model_validate(item) for item in resp.data]
            return AsyncPage(data=data, meta=resp.meta, request_id=resp.request_id, fetcher=fetch)

        return await fetch(page)

    async def retrieve(self, agent_id: str, conversation_id: str) -> Conversation:
        resp = await self._client.request(_retrieve_conversation_spec(agent_id, conversation_id))
        return Conversation.model_validate(resp.data)
