# bimpeai

Official Python SDK for the BimpeAI Agent Console API. It ships a synchronous client and an asynchronous one that share the same surface, with request and response types modelled in Pydantic and HTTP handled by httpx. Requires Python 3.10 or newer.

## Install

```bash
pip install bimpeai
# or: uv add bimpeai
```

The only runtime dependencies are httpx, pydantic v2, and typing-extensions.

## Quickstart

```python
from bimpeai import BimpeAI

client = BimpeAI(api_key="sk_...")
for agent in client.agents.list(limit=50):
    print(agent.id, agent.name)
```

The async client mirrors it. Construct `AsyncBimpeAI`, await each call, and use `async for` to walk a list.

```python
import asyncio

from bimpeai import AsyncBimpeAI


async def main() -> None:
    async with AsyncBimpeAI(api_key="sk_...") as client:
        page = await client.agents.list(limit=50)
        async for agent in page:
            print(agent.id, agent.name)


asyncio.run(main())
```

## Authentication

Pass your team API key when you construct the client. The SDK sends it as `Authorization: Bearer <key>`; keys are prefixed `sk_`. The key is required, and constructing a client with an empty key raises `UserError` before any request goes out. The SDK does not read the key from the environment, so if you keep it in a variable like `BIMPEAI_API_KEY`, read it yourself and pass it in.

```python
import os

client = BimpeAI(api_key=os.environ["BIMPEAI_API_KEY"])
```

A scope-restricted key works the same way. A call that falls outside the key's scope comes back as `PermissionDeniedError`.

## Clients and lifecycle

Both clients open an httpx client and own it for their lifetime. Use them as context managers so the connection pool is closed when you are done.

```python
with BimpeAI(api_key="sk_...") as client:
    client.agents.list()

async with AsyncBimpeAI(api_key="sk_...") as client:
    await client.agents.list()
```

If you would rather manage the lifetime yourself, call `client.close()` on the sync client or `await client.aclose()` on the async one. You can also hand in your own httpx client through the `http_client` argument, in which case the SDK uses it and leaves closing it to you.

```python
import httpx

with httpx.Client(proxy="http://localhost:8080") as http:
    client = BimpeAI(api_key="sk_...", http_client=http)
    client.agents.list()
```

Every client exposes four resources: `agents`, `workflows`, `conversations`, and `calls`.

## Agents

```python
agents = client.agents.list(page=2, limit=50, search="support", sort="-created_at")
agent = client.agents.create(name="Support bot", description="Tier 1 support", idempotency_key="op-1")
detail = client.agents.retrieve(agent.id)
client.agents.update(agent.id, description="Now tier 2 as well")
```

`list` returns a `Page[Agent]`. `create` and `update` take the agent fields as keyword arguments (`name`, `description`, `system_prompt`, `language`, `persona`, `agent_workflow_id`, `rules`, `timezone`, `logo`, the `business_*` fields, and `escalation_email`); only `name` is required on create, and every field is optional on update. `create` and `update` return an `Agent`, while `retrieve` returns an `AgentDetail`, which is an `Agent` plus the agent's integrations, channels, conversation flows, actions, and knowledge bases inlined.

The read-only sub-resources each return a plain list.

```python
client.agents.integrations.list(agent_id)
client.agents.channels.list(agent_id)
client.agents.conversation_flows.list(agent_id)
client.agents.actions.list(agent_id)
```

Knowledge bases support full CRUD. The create body is a text source or a URL source, distinguished by its `type`, and is passed as a single dict so the union stays well typed.

```python
client.agents.knowledge_bases.list(agent_id)
client.agents.knowledge_bases.create(agent_id, {"type": "text", "name": "FAQ", "content": "..."})
client.agents.knowledge_bases.create(agent_id, {"type": "url", "name": "Docs", "url": "https://..."})
client.agents.knowledge_bases.update(agent_id, kb_id, description="Updated")
client.agents.knowledge_bases.delete(agent_id, kb_id)
```

## Workflows

```python
workflows = client.workflows.list(scope="public", search="triage", sort="-created_at")
workflow = client.workflows.create(name="Triage", idempotency_key="op-2")
client.workflows.retrieve(workflow.id)
client.workflows.update(workflow.id, tags=["v2"])
client.workflows.delete(workflow.id)
```

`scope` is either `owned` or `public`. `list` returns a `Page[WorkflowSummary]`; `retrieve`, `create`, and `update` return a `Workflow`, which is the summary plus `system_prompt`, `rules`, `flows`, `tags`, and `prompt_config`. As with agents, create and update take the fields as keyword arguments and only `name` is required on create.

## Conversations and messages

```python
conversations = client.conversations.list(agent_id, channel="whatsapp", search="invoice")
conversation = client.conversations.retrieve(agent_id, conversation_id)

messages = client.conversations.messages.list(agent_id, conversation_id)
sent = client.conversations.messages.send(agent_id, conversation_id, message="Hello")
```

`channel` accepts `whatsapp`, `messenger`, `instagram`, `webchat`, and the `test_*` variants of each. `conversations.list` returns a `Page[Conversation]` and `messages.list` returns a `Page[Message]`. `send` takes `message` and optional `attachments` (each `{"type": ..., "url": ...}`) and returns the created `Message`.

## Streaming messages

New messages in a conversation can be streamed in real time over Server-Sent Events. The flow has two steps. First the SDK asks the `stream-ticket` endpoint for a single-use, short-lived ticket. Then it opens a `GET` to the message-stream endpoint carrying that ticket as a query parameter, with `Accept: text/event-stream`. The stream is authenticated by the ticket, not the bearer key, so the API key never travels on the long-lived connection. `stream` runs both steps and yields messages as they arrive.

```python
for message in client.conversations.messages.stream(agent_id, conversation_id):
    print(message.role, message.message)
```

Each value is a `StreamMessageEvent` with `id`, `conversation_id`, `role`, `message`, `message_type`, and `created_at`. The server also sends periodic heartbeat events to keep the connection open; the SDK consumes those itself and never yields them, so the loop only sees real messages.

If the connection drops, the SDK reconnects on its own. It remembers the id of the last message it gave you and resumes from there, so you neither miss a message nor see one twice. The retry budget counts consecutive failures and resets every time a message is delivered, so a stream that runs for hours before a blip still has its full set of retries. Set `reconnect=False` to stop instead of reconnecting when the server closes the stream, `max_retries` to change the reconnect budget (default 5), `after` to replay messages created after a given chat id or ISO-8601 timestamp, and `timeout` to bound the read. Stop a stream by breaking out of the loop.

The async client returns an async iterator with the same options.

```python
async for message in client.conversations.messages.stream(agent_id, conversation_id):
    print(message.role, message.message)
```

The ticket step is available on its own if you want to open the stream yourself. The ticket is single-use and expires after `expires_in` seconds.

```python
ticket = client.conversations.messages.stream_ticket(agent_id, conversation_id)
print(ticket.ticket, ticket.expires_in)
```

## Calls

`calls.list()` is wired up, but the API answers with 501 today, so it raises `APINotImplementedError`. The call site will keep working and start returning data once the endpoint ships, without an SDK change.

```python
from bimpeai import APINotImplementedError

try:
    client.calls.list()
except APINotImplementedError:
    ...  # not available yet
```

## Pagination

Every `list` returns a `Page` (or `AsyncPage` on the async client). A page carries the items for the current page in `data`, the `meta` block, and the `request_id` of the response that produced it. The `meta` is a `PaginationMeta` with `total_count`, `page_count`, `current_page`, `limit`, `has_next_page`, and `has_previous_page`.

```python
page = client.agents.list(limit=50)
page.data            # list[Agent] for this page
page.meta.total_count if page.meta else 0
page.request_id      # str | None
page.has_next_page   # bool
next_page = page.get_next_page()  # Page[Agent] | None
```

Iterating the page walks every item across every page, fetching the next page only when the current one runs out.

```python
for agent in client.agents.list(limit=50):
    print(agent.id)
```

If you want the page objects rather than the items, iterate `pages()`.

```python
for page in client.agents.list().pages():
    print(page.meta.current_page if page.meta else None)
```

On the async client these become `async for` and `await page.get_next_page()`.

## Errors

Every error raised by the SDK subclasses `BimpeAIError`. A `UserError` means the SDK rejected something before sending it, such as an empty API key. A connection that never produced a response raises `APIConnectionError`, and a timeout raises `APITimeoutError`, which is a subclass of it. Everything the server returned as an error subclasses `APIError`.

```python
from bimpeai import RateLimitError, ValidationError

try:
    client.agents.create(name="")
except ValidationError as err:
    for field in err.field_errors:
        print(field["path"], field["message"])
except RateLimitError as err:
    print("retry after", err.retry_after, "seconds")
```

The hierarchy:

```
BimpeAIError
├── UserError
├── APIConnectionError
│   └── APITimeoutError
└── APIError
    ├── BadRequestError
    │   └── ValidationError
    ├── AuthenticationError
    ├── PermissionDeniedError
    ├── NotFoundError
    ├── ConflictError
    ├── RateLimitError
    ├── InternalServerError
    └── APINotImplementedError
```

Every `APIError` carries `status`, `code`, `request_id`, `headers`, and the raw `body`. `code` is one of the `ErrorCode` values (`validation_error`, `bad_request`, `unauthorized`, `api_key_missing`, `api_key_invalid`, `api_key_expired`, `insufficient_scope`, `forbidden`, `not_found`, `conflict`, `rate_limited`, `too_many_requests`, `not_implemented`, `agent_limit_reached`, `internal_error`). `ValidationError` adds `field_errors`, a list of `{"path", "message"}` dicts. `RateLimitError` adds `retry_after`, `limit`, `remaining`, and `reset_at`, read from the `Retry-After` and `X-RateLimit-*` response headers.

## Retries and idempotency

By default the SDK retries up to twice. It retries connection errors and timeouts, and the status codes 408, 429, and any 5xx other than 501; it never retries 409 or 501. Backoff is exponential with full jitter, and a 429 honours the `Retry-After` header. Change the budget per client or per call.

```python
client = BimpeAI(api_key="sk_...", max_retries=3)
client.agents.create(name="A", max_retries=0)  # this call only
```

Write requests accept an `idempotency_key`. When retries are on and you do not supply one, the SDK generates a key once per call and reuses it across attempts, so a retried write cannot create a duplicate. The key is sent as the `Idempotency-Key` header.

```python
client.agents.create(name="A", idempotency_key="create-A-2026-06-14")
```

## Per-call options

The write methods (`agents.create`, `agents.update`, `agents.knowledge_bases.create`, `agents.knowledge_bases.update`, `workflows.create`, `workflows.update`, `conversations.messages.send`, and `conversations.messages.stream_ticket`) accept `idempotency_key`, `timeout`, `max_retries`, and `headers` as keyword arguments alongside the body. Each overrides the client-level setting for that one call. `headers` is merged into the request headers, which is the seam for sending a request id you control through `X-Request-Id`.

## Configuration

```python
BimpeAI(
    api_key="sk_...",                  # required
    base_url="https://api.bimpe.ai",   # default
    timeout=30.0,                       # seconds, per request
    max_retries=2,
    default_headers=None,               # sent on every request
    http_client=None,                   # inject an httpx.Client / AsyncClient
)
```

`AsyncBimpeAI` takes the same arguments; only `http_client` differs, expecting an `httpx.AsyncClient`. The SDK targets the `/api/v1/console` paths under `base_url`, and identifies itself with a User-Agent like `bimpeai-python/<version> (Python/<py>; <os>)`.

## Types

Response models are Pydantic models that are frozen and tolerant of unknown fields, so a new field added server-side will not break deserialization and is reachable as an attribute. Request bodies are TypedDicts, and the create and update methods accept them as typed keyword arguments via `Unpack`, so a type checker flags an unknown or mistyped field at the call site.

## Requirements

Python 3.10, 3.11, 3.12, 3.13, and 3.14 are supported and tested.

## License

MIT
