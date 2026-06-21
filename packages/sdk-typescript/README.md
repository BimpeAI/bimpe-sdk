# @bimpeai/sdk

Official TypeScript SDK for the BimpeAI Agent Console API. It has no runtime dependencies and is built on the platform `fetch`, so it runs on Node 24+, Bun, Deno, modern browsers, Cloudflare Workers, and Vercel Edge. Requests and responses are fully typed, and the package ships both ESM and CommonJS with bundled type declarations.

## Install

```bash
pnpm add @bimpeai/sdk
# npm install @bimpeai/sdk
# yarn add @bimpeai/sdk
```

## Quickstart

```ts
import { BimpeAI } from '@bimpeai/sdk';

const bimpe = new BimpeAI({ apiKey: process.env.BIMPEAI_API_KEY! });

const agents = await bimpe.agents.list();
for (const agent of agents.data) console.log(agent.id, agent.name);
```

## Authentication

Pass your team API key when you construct the client. The SDK sends it as `Authorization: Bearer <key>`; keys are prefixed `sk_`. The key is required, and constructing a client without one throws `UserError` before any request goes out. The SDK does not read the key from the environment, so read it yourself and pass it in.

```ts
const bimpe = new BimpeAI({ apiKey: 'sk_…' });
```

A scope-restricted key (for example one limited to `workflows:read`) works the same way. A call that falls outside the key's scope throws `PermissionDeniedError`.

## Resources

The client exposes four resources: `agents`, `workflows`, `conversations`, and `calls`. Every method returns a typed result, and the list methods return a value you can both await and iterate (see Pagination).

### Agents

```ts
await bimpe.agents.list({ page: 2, limit: 50, search: 'support', sort: '-created_at' });
const agent = await bimpe.agents.create(
  { workflow_id: 'wf_abc', name: 'Support bot', description: 'Tier 1 support' },
  { idempotencyKey: 'op-1' },
);
const detail = await bimpe.agents.retrieve(agent.id);
await bimpe.agents.update(agent.id, { description: 'Updated' });
await bimpe.agents.updateLiveStatus(agent.id, { status: 'live' });
```

`list` returns a `PagePromise<Agent>`. `create` requires `workflow_id`, `name`, and `description`, and returns an `AgentCreateResponse` (includes optional nested `workflow`). `retrieve` returns an `AgentDetail` with `integrations`, `channels`, and `knowledge_bases` summaries. Only `create` and message sends accept per-call `RequestOptions` on writes where noted.

```ts
await bimpe.agents.integrations.list(agentId);
await bimpe.agents.channels.list(agentId);
await bimpe.agents.actions.list(agentId);
await bimpe.agents.actions.enable(agentId, { action_ids: ['ac_1'] });
await bimpe.agents.actions.disable(agentId, { action_ids: ['ac_1'] });
```

Knowledge bases support full CRUD. The create body is a text source or a URL source, told apart by its `type`.

```ts
await bimpe.agents.knowledgeBases.list(agentId);
await bimpe.agents.knowledgeBases.create(agentId, { type: 'text', name: 'FAQ', content: '…' });
await bimpe.agents.knowledgeBases.create(agentId, { type: 'url', name: 'Docs', url: 'https://…' });
await bimpe.agents.knowledgeBases.update(agentId, kbId, { description: '…' });
await bimpe.agents.knowledgeBases.delete(agentId, kbId);
```

### Workflows

```ts
await bimpe.workflows.list({ scope: 'accessible', search: 'triage', sort: '-created_at' });
const workflow = await bimpe.workflows.create(
  { name: 'Triage', system_prompt: 'You are helpful…' },
  { idempotencyKey: 'op-2' },
);
const cloned = await bimpe.workflows.clone({ source_workflow_id: workflow.id });
await bimpe.workflows.retrieve(workflow.id);
await bimpe.workflows.update(workflow.id, { tags: ['v2'] });
await bimpe.workflows.delete(workflow.id);
```

`scope` is `accessible` (default), `owned`, or `public`. `list` returns a `PagePromise<Workflow>` with the full workflow shape. Only `create` and `clone` accept per-call `RequestOptions`.

### Conversations and messages

```ts
await bimpe.conversations.list(agentId, {
  channel: 'whatsapp',
  is_test_channel: false,
  needs_attention: true,
});
await bimpe.conversations.retrieve(agentId, conversationId);
await bimpe.conversations.updateAiStatus(agentId, conversationId, { is_ai_chat_paused: true });

await bimpe.conversations.messages.list(agentId, conversationId);
const sent = await bimpe.conversations.messages.send(agentId, conversationId, {
  message: 'Hello',
  role: 'user',
});
const opened = await bimpe.conversations.createOrSendMessage(agentId, {
  message: 'Hello',
  channel_type: 'whatsapp',
  channel_user_id: '+2348012345678',
});
```

`channel` accepts `whatsapp`, `webchat`, `telephony`, and `test_*` variants. `conversations.list` returns a `PagePromise<ConversationListItem>`; `retrieve` returns a full `Conversation`. `send` takes `SendMessageBody` (`message` plus optional `role`). `createOrSendMessage` accepts either `conversation_id` or `channel_type` + `channel_user_id`.

### Streaming messages

Stream new messages in a conversation in real time over Server-Sent Events. The flow has two steps. First the SDK issues a single-use, short-lived ticket from the `stream-ticket` endpoint. Then it opens a `GET` to the message-stream endpoint with that ticket as a query parameter and `Accept: text/event-stream`. The stream is authenticated by the ticket rather than the bearer key, so your API key never travels on the long-lived connection and the stream can be opened from a browser. `stream()` does both steps for you and yields messages as they arrive.

```ts
const controller = new AbortController();

for await (const message of bimpe.conversations.messages.stream(agentId, conversationId, {
  signal: controller.signal,
})) {
  console.log(message.role, message.message);
}
```

Each yielded value is a `StreamMessageEvent` with `id`, `conversation_id`, `role`, `message`, `message_type`, and `created_at`. The server also emits periodic `heartbeat` events to hold the connection open; the SDK consumes those internally and never yields them, so the loop only ever sees real messages.

On a dropped connection the SDK reconnects on its own. It remembers the id of the last message it handed you and resumes from there using `after`, so you neither miss a message nor see one twice. The reconnect budget counts consecutive failures and resets to zero every time a message is delivered, so a stream that flows for hours and then blips still gets a full set of retries rather than one exhausted long ago. Reconnects use the same backoff-with-jitter policy as the rest of the SDK.

The options are `after` to replay messages created after a chat id or ISO-8601 timestamp (this is also what resume uses under the hood), `reconnect` to re-open after a drop (default `true`; set `false` to end iteration when the server closes the stream), `maxRetries` for the maximum consecutive reconnect attempts before giving up (default `5`), and `signal` to stop the stream by aborting. Breaking out of the loop stops it too. The async iterable never rejects on a normal close; it just ends.

The ticket step is exposed on its own if you want to open the stream yourself; the ticket is single-use and expires after `expires_in` seconds.

```ts
const { ticket, expires_in } = await bimpe.conversations.messages.streamTicket(agentId, conversationId);
```

### Calls

`calls.list()` may throw `NotImplementedError` until the API ships. `calls.make(body)` and `calls.queue(body)` POST placeholder endpoints that echo the body with `code: not_implemented`.

## Pagination

Every `list` returns a `PagePromise`, which is both a promise and an async iterable. Await it to get a single `Page`, or iterate it with `for await` to walk every item across pages, fetching the next page only when the current one runs out.

```ts
// One page
const page = await bimpe.agents.list({ limit: 50 });
page.data;        // readonly Agent[]
page.meta;        // PaginationMeta | null
page.requestId;   // string | null
page.hasNextPage; // boolean
const next = await page.getNextPage(); // Page<Agent> | null

// Every item, fetching pages on demand
for await (const agent of bimpe.agents.list({ limit: 50 })) {
  console.log(agent.id);
}

// Page by page
for await (const page of bimpe.agents.list().pages()) {
  console.log(page.meta?.current_page);
}
```

`PaginationMeta` carries `total_count`, `page_count`, `current_page`, `limit`, `has_next_page`, and `has_previous_page`.

## Request ids

Every request is tagged with an `X-Request-Id` (a UUID the SDK generates, or one you supply through `headers`). The id from the response is on `page.requestId`, on `error.requestId` for any `ApiError`, and on `ApiResponse.requestId` when you use the escape hatch. Quote it when you contact support about a specific call.

## Errors

Every error the SDK throws extends `BimpeAIError`. A `UserError` means the SDK rejected something before sending it, such as a missing API key. A request that never produced a response throws `ConnectionError`, and a timeout throws `ConnectionTimeoutError`, which extends it. Everything the server returned as an error extends `ApiError`.

```ts
import { RateLimitError, ValidationError } from '@bimpeai/sdk';

try {
  await bimpe.agents.create({ name: '' });
} catch (error) {
  if (error instanceof ValidationError) {
    for (const field of error.fieldErrors) console.warn(`${field.path}: ${field.message}`);
  } else if (error instanceof RateLimitError) {
    console.warn(`retry in ${error.retryAfter}s`);
  } else {
    throw error;
  }
}
```

The hierarchy:

```
BimpeAIError
├── UserError
├── ConnectionError
│   └── ConnectionTimeoutError
└── ApiError
    ├── BadRequestError
    │   └── ValidationError
    ├── AuthenticationError
    ├── PermissionDeniedError
    ├── NotFoundError
    ├── ConflictError
    ├── RateLimitError
    ├── InternalServerError
    └── NotImplementedError
```

Every `ApiError` carries `status`, `code`, `requestId`, `headers`, and the raw `body`. `code` is one of the `ErrorCode` values (`validation_error`, `bad_request`, `unauthorized`, `api_key_missing`, `api_key_invalid`, `api_key_expired`, `insufficient_scope`, `forbidden`, `not_found`, `conflict`, `rate_limited`, `too_many_requests`, `not_implemented`, `agent_limit_reached`, `internal_error`), or `null` if the server sent none. `ValidationError` adds `fieldErrors`, an array of `{ path, message }`. `RateLimitError` adds `retryAfter` (seconds), `limit`, `remaining`, and `resetAt` (a `Date`), read from the `Retry-After` and `X-RateLimit-*` headers.

## Retries and idempotency

By default the SDK retries up to twice. It retries connection errors and timeouts, and the status codes 408, 429, and any 5xx other than 501; it never retries 409 or 501. Backoff is exponential with full jitter, and a 429 honours the `Retry-After` header.

```ts
const bimpe = new BimpeAI({ apiKey: '…', maxRetries: 3 });
await bimpe.agents.create(body, { maxRetries: 0 }); // this call only
```

Write requests accept an `idempotencyKey`. When retries are on and you do not supply one, the SDK generates a key once per call and reuses it across attempts, so a retried write cannot create a duplicate. The key is sent as the `Idempotency-Key` header on writes only.

```ts
await bimpe.agents.create({ name: 'A' }, { idempotencyKey: 'create-A-2026-06-14' });
```

## Per-call options

The methods that accept a second `options` argument (`agents.create`, `agents.knowledgeBases.create`, `workflows.create`, and `conversations.messages.send`, plus `streamTicket`) take a `RequestOptions`: `idempotencyKey`, `signal` (an `AbortSignal`), `timeout`, `maxRetries`, and `headers`. Each overrides the client-level setting for that one call, and `headers` is merged over the client's default headers.

## Configuration

```ts
new BimpeAI({
  apiKey: string,                 // required
  baseUrl?: string,               // default 'https://api.bimpe.ai'
  timeout?: number,               // per-request ms; default 30_000
  maxRetries?: number,            // default 2
  fetch?: typeof fetch,           // override for tests or edge runtimes
  defaultHeaders?: Record<string, string>,
  logger?: { debug; warn },       // structured hooks; off by default
});
```

The SDK targets the `/api/v1/console` paths under `baseUrl`, and identifies itself with a User-Agent like `bimpeai-sdk-typescript/<version> (<runtime>; <platform>)`. The `logger` hooks, if provided, receive a message and an optional context object on `debug` and `warn`; nothing is logged by default. The exported `VERSION` constant holds the package version.

## Escape hatch

For endpoints the SDK does not model yet, call the transport directly. It applies the same auth, base URL, retries, and request id as the typed methods, and returns the full `ApiResponse<T>` with `data`, `meta`, `requestId`, `status`, and `headers`.

```ts
const res = await bimpe.request<{ pong: boolean }>({ method: 'GET', path: '/health' });
res.data.pong;
```

## Runtime support

Runs on Node 24+, Bun, Deno, modern browsers, Cloudflare Workers, and Vercel Edge. It uses `fetch`, `AbortController`, web streams for SSE, and `crypto.randomUUID` where available. On a runtime without `fetch` in the global scope, pass one in through the `fetch` option. Ships as ESM and CommonJS with subpath exports and bundled type declarations, and is marked side-effect free for tree shaking.

## Types

Every request body and response is exported as a type, so you can annotate your own code against the SDK. Response objects tolerate unknown fields, so a field added server-side will not break parsing. Request bodies are the `Create*`/`Update*` types, with required and optional fields encoded in the type, so a mistyped or missing field is a compile error at the call site.

## Versioning

Pre-1.0, minor versions may include breaking changes. See `CHANGELOG.md` for each release.

Prereleases are published from the `staging` branch under the `beta` dist-tag. Install the latest prerelease with `pnpm add @bimpeai/sdk@beta`.

## License

MIT
