# @bimpeai/sdk

## 0.1.0

### Minor Changes

- [`bafa334`](https://github.com/BimpeAI/bimpe-sdk/commit/bafa33446f5d43a864032d132ed431f3ee599150) Thanks [@Theshedman](https://github.com/Theshedman)! - Initial release of the BimpeAI TypeScript SDK: typed coverage for Agents, Workflows, Conversations, and Messages, with built-in retries, idempotency, lazy pagination, and a typed error hierarchy. The Calls resource is wired but throws NotImplementedError until the upstream endpoint ships.

- [#1](https://github.com/BimpeAI/bimpe-sdk/pull/1) [`43f5948`](https://github.com/BimpeAI/bimpe-sdk/commit/43f594893b3a7c8c2cedeb4ff31ee37608e2b704) Thanks [@Theshedman](https://github.com/Theshedman)! - Add live conversation message streaming over Server-Sent Events: `conversations.messages.stream()` issues a ticket, opens the stream, yields each message, handles heartbeats, and auto-reconnects from the last seen message; `conversations.messages.streamTicket()` exposes the ticket step. Also export an `ErrorCode` union of the known envelope codes, including `too_many_requests`.

### Patch Changes

- [#1](https://github.com/BimpeAI/bimpe-sdk/pull/1) [`4136ee1`](https://github.com/BimpeAI/bimpe-sdk/commit/4136ee19d6bd89a61f4003f94329c0fd42bdcab2) Thanks [@Theshedman](https://github.com/Theshedman)! - Point the default base URL at `https://api.bimpe.ai`, so a client constructed without an explicit `baseUrl` reaches the live API.
