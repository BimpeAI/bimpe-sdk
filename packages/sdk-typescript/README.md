# @bimpeai/sdk

Official TypeScript SDK for the BimpeAI Agent Console API. Zero runtime dependencies. Runs on Node 24+, Bun, Deno, modern browsers, and edge runtimes.

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

The SDK sends your team API key as `Authorization: Bearer <key>`. Keys are prefixed `sk_`.

```ts
const bimpe = new BimpeAI({ apiKey: 'sk_…' });
```

Scope-restricted keys (for example `workflows:read`) work the same way; a call outside the key's scope throws `PermissionDeniedError`.

## Resources

### Agents

```ts
await bimpe.agents.list({ page: 2, limit: 50, sort: '-created_at' });
await bimpe.agents.create({ name: 'Support bot' }, { idempotencyKey: 'op-1' });
await bimpe.agents.retrieve(agentId);
await bimpe.agents.update(agentId, { description: 'Updated' });

await bimpe.agents.integrations.list(agentId);
await bimpe.agents.channels.list(agentId);
await bimpe.agents.conversationFlows.list(agentId);
await bimpe.agents.actions.list(agentId);

await bimpe.agents.knowledgeBases.list(agentId);
await bimpe.agents.knowledgeBases.create(agentId, { type: 'text', name: 'FAQ', content: '…' });
await bimpe.agents.knowledgeBases.update(agentId, kbId, { description: '…' });
await bimpe.agents.knowledgeBases.delete(agentId, kbId);
```

### Workflows

```ts
await bimpe.workflows.list({ scope: 'public' });
await bimpe.workflows.create({ name: 'Triage' });
await bimpe.workflows.retrieve(id);
await bimpe.workflows.update(id, { tags: ['v2'] });
await bimpe.workflows.delete(id);
```

### Conversations and messages

```ts
await bimpe.conversations.list(agentId, { channel: 'whatsapp' });
await bimpe.conversations.retrieve(agentId, conversationId);
await bimpe.conversations.messages.list(agentId, conversationId);
await bimpe.conversations.messages.send(agentId, conversationId, { message: 'Hello' });
```

### Streaming messages

Stream new messages in a conversation in real time over Server-Sent Events. `stream()` issues a single-use ticket, opens the stream, and yields each message; heartbeats are handled internally, and a dropped connection automatically reconnects and resumes from the last message seen.

```ts
const controller = new AbortController();

for await (const message of bimpe.conversations.messages.stream(agentId, conversationId, {
  signal: controller.signal,
})) {
  console.log(message.role, message.message);
}
```

Options: `after` (replay from a chat id or ISO timestamp), `reconnect` (default true), `maxRetries` (consecutive reconnects, default 5), and `signal`. Stop the stream by aborting the signal or `break`-ing the loop. The ticket step is also exposed on its own:

```ts
const { ticket, expires_in } = await bimpe.conversations.messages.streamTicket(agentId, conversationId);
```

### Calls

`calls.list()` is wired but the API answers with 501 today, so it throws `NotImplementedError`. It will start returning data once the endpoint ships, without an SDK change to your call site.

## Pagination

`list` returns a value you can both await and iterate. Await it for a single `Page`; iterate it with `for await` to walk every item across pages, fetching lazily.

```ts
// One page
const page = await bimpe.agents.list({ limit: 50 });
page.data; // ReadonlyArray<Agent>
page.meta; // PaginationMeta
page.requestId; // string | null
page.hasNextPage; // boolean
const next = await page.getNextPage();

// Every item, fetching pages on demand
for await (const agent of bimpe.agents.list({ limit: 50 })) {
  console.log(agent.id);
}

// Page by page
for await (const page of bimpe.agents.list().pages()) {
  console.log(page.meta?.current_page);
}
```

## Errors

Every SDK error extends `BimpeAIError`. Server responses extend `ApiError`.

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

Every `ApiError` carries `status`, `code`, `requestId`, `headers`, and the raw `body`. `RateLimitError` adds `retryAfter`, `limit`, `remaining`, and `resetAt`. `ValidationError` adds `fieldErrors`.

## Retries and idempotency

By default the SDK retries up to twice on connection errors, timeouts, 408, 429, and 5xx (never 409 or 501), with exponential backoff and full jitter. A 429 honours `Retry-After`.

```ts
const bimpe = new BimpeAI({ apiKey: '…', maxRetries: 3 });
await bimpe.agents.create(body, { maxRetries: 0 }); // override per call
```

Writes accept an `idempotencyKey`. When retries are on and you do not supply one, the SDK generates a key once per call and reuses it across attempts, so a retried write cannot create a duplicate.

```ts
await bimpe.agents.create({ name: 'A' }, { idempotencyKey: 'create-A-2026-06-06' });
```

## Configuration

```ts
new BimpeAI({
  apiKey: string,                 // required
  baseUrl?: string,               // default 'https://api.bimpeai.com'
  timeout?: number,               // per-request ms; default 30_000
  maxRetries?: number,            // default 2
  fetch?: typeof fetch,           // override for tests or edge runtimes
  defaultHeaders?: Record<string, string>,
  logger?: { debug; warn },       // structured hooks; off by default
});
```

Per-call options on writes: `idempotencyKey`, `signal`, `timeout`, `maxRetries`, `headers`.

## Escape hatch

For endpoints the SDK does not model yet, call the transport directly.

```ts
const res = await bimpe.request<{ pong: boolean }>({ method: 'GET', path: '/health' });
```

## Runtime support

Node 24+, Bun, Deno, modern browsers, Cloudflare Workers, and Vercel Edge. Ships as ESM and CJS with subpath exports and bundled type declarations.

## Versioning

Pre-1.0, minor versions may include breaking changes. See `CHANGELOG.md` for each release.

## License

MIT
