# bimpeai

Official Python SDK for the BimpeAI Agent Console API. Synchronous and asynchronous clients, typed with Pydantic, over httpx. Python 3.10+.

## Install

```bash
pip install bimpeai
# or: uv add bimpeai
```

## Quickstart

```python
from bimpeai import BimpeAI

client = BimpeAI(api_key="sk_...")
for agent in client.agents.list(limit=50):
    print(agent.id, agent.name)
```

Async:

```python
import asyncio

from bimpeai import AsyncBimpeAI


async def main() -> None:
    async with AsyncBimpeAI(api_key="sk_...") as client:
        async for agent in await client.agents.list():
            print(agent.id, agent.name)


asyncio.run(main())
```

## Authentication

The SDK sends your team API key as `Authorization: Bearer <key>` (keys are prefixed `sk_`). Scope-restricted keys raise `PermissionDeniedError` when a call is out of scope.

## Resources

```python
client.agents.list(page=2, limit=50, sort="-created_at")
client.agents.create(name="Support bot", idempotency_key="op-1")
client.agents.retrieve(agent_id)
client.agents.update(agent_id, description="...")
client.agents.integrations.list(agent_id)
client.agents.channels.list(agent_id)
client.agents.conversation_flows.list(agent_id)
client.agents.actions.list(agent_id)
client.agents.knowledge_bases.list(agent_id)
client.agents.knowledge_bases.create(agent_id, {"type": "text", "name": "FAQ", "content": "..."})
client.agents.knowledge_bases.update(agent_id, kb_id, description="...")
client.agents.knowledge_bases.delete(agent_id, kb_id)

client.workflows.list(scope="public")
client.workflows.create(name="Triage")
client.workflows.retrieve(workflow_id)
client.workflows.update(workflow_id, tags=["v2"])
client.workflows.delete(workflow_id)

client.conversations.list(agent_id, channel="whatsapp")
client.conversations.retrieve(agent_id, conversation_id)
client.conversations.messages.list(agent_id, conversation_id)
client.conversations.messages.send(agent_id, conversation_id, message="Hello")
```

The async client (`AsyncBimpeAI`) exposes the same tree; `list` becomes `async for` and every call is awaited.

## Pagination

`list` returns a `Page`/`AsyncPage`. Iterate it to walk every item across pages (fetched lazily), or use `.data`, `.meta`, `.has_next_page`, `.get_next_page()`, and `.pages()`.

```python
page = client.agents.list(limit=50)
print(page.meta.total_count if page.meta else 0)
for agent in page:  # auto-paginates
    ...
```

## Errors

Every error subclasses `BimpeAIError`. Server errors subclass `APIError` (`status`, `code`, `request_id`, `headers`, `body`).

```python
from bimpeai import RateLimitError, ValidationError

try:
    client.agents.create(name="")
except ValidationError as err:
    for field in err.field_errors:
        print(field["path"], field["message"])
except RateLimitError as err:
    print("retry in", err.retry_after)
```

Hierarchy: `BimpeAIError` → `APIConnectionError`/`APITimeoutError`, and `APIError` → `BadRequestError`/`ValidationError`, `AuthenticationError`, `PermissionDeniedError`, `NotFoundError`, `ConflictError`, `RateLimitError`, `InternalServerError`, `APINotImplementedError`.

## Retries and idempotency

By default the SDK retries up to twice on connection errors, timeouts, 408, 429, and 5xx (never 409 or 501), with exponential backoff and full jitter; 429 honors `Retry-After`. Writes accept `idempotency_key`; when retries are on and none is supplied, one is generated per call and reused across attempts.

```python
client = BimpeAI(api_key="sk_...", max_retries=3)
client.agents.create(name="A", max_retries=0)
```

## Streaming

```python
for message in client.conversations.messages.stream(agent_id, conversation_id):
    print(message.role, message.message)
```

`stream` issues a ticket, opens the SSE stream, yields each message, handles heartbeats, and reconnects from the last message on a drop (`reconnect=False` to disable, `after=` to replay). The async client returns an `async for` iterator.

## Configuration

```python
BimpeAI(
    api_key="sk_...",        # required
    base_url="https://api.bimpeai.com",
    timeout=30.0,            # seconds
    max_retries=2,
    default_headers=None,
    http_client=None,        # inject an httpx.Client / AsyncClient
)
```

## License

MIT
