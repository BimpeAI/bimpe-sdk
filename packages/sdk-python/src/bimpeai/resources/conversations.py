from __future__ import annotations

from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, Protocol

import httpx
from typing_extensions import Unpack

from .._models import ApiResponse
from .._request import RequestOptions, RequestSpec, StreamSpec
from ..pagination import AsyncPage, Page
from ..types.conversations import Conversation, ConversationChannel, Message, SendMessageBody


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
