# @bimpeai/sdk

## 0.3.0

### Minor Changes

- [#12](https://github.com/BimpeAI/bimpe-sdk/pull/12) [`ffd8e40`](https://github.com/BimpeAI/bimpe-sdk/commit/ffd8e404a00b8f901d5e38219efd50d42cdb3eb7) Thanks [@Theshedman](https://github.com/Theshedman)! - Add the agent integrations subsystem and the test-code endpoint. `agents.getTestCode` returns the agent's test code and the per-channel deep links used to start a test conversation. `agents.integrations` becomes writable through four connector families, each with `list`, `configure`, and `disconnect`: `bimpeai` for first-party connectors (Google Calendar, Stripe, Paystack, Google Sheets, Bumpa), `customApi` for custom HTTP APIs with a nested `tools` sub-resource, `mcpServer` for MCP servers with `discover`, `test`, and a `tools` listing, and `pipedream` for OAuth onboarding. The existing read-only `integrations.list` is unchanged.

- [#12](https://github.com/BimpeAI/bimpe-sdk/pull/12) [`b4f5b50`](https://github.com/BimpeAI/bimpe-sdk/commit/b4f5b500e7ebed53296d5088237456e433f993b5) Thanks [@Theshedman](https://github.com/Theshedman)! - Add a team-scoped `phoneNumbers` resource. `phoneNumbers.list`, `retrieve`, and `update` manage number assignments (linking a number to an agent and labelling it), and a nested `phoneNumbers.requests.list`/`create` lists and submits provisioning requests. A number linked to an agent is the live telephony channel that `calls.make({ is_test_call: false })` dials out over.

## 0.2.0

### Minor Changes

- [#9](https://github.com/BimpeAI/bimpe-sdk/pull/9) [`7b0f709`](https://github.com/BimpeAI/bimpe-sdk/commit/7b0f709fc5502df5242e88d9bb96ef8c1996def6) Thanks [@Theshedman](https://github.com/Theshedman)! - Align the SDK with Console API v1.

  Breaking: `agents.create` now takes `workflow_id` (and `system_prompt`/`rules` are gone), `persona` is an enum, and it returns an `AgentCreateResponse` carrying the nested workflow; the `Agent` read type renames `agent_workflow_id` to `workflow_id` and drops `system_prompt`/`rules`, and `AgentDetail` is reshaped (nested `knowledge_bases`/`integrations`/`channels`, with `conversation_flow` and `actions` removed); `agents.conversationFlows` is removed; the knowledge base methods return the fuller `KnowledgeBaseItem`; `conversations.retrieve` returns a `ConversationDetail` distinct from the list item; sending a message no longer accepts `attachments` (they still appear on message responses); the conversation channel set drops `messenger` and `instagram` and adds `telephony` and `test_webchat`; calls are now agent-scoped and live, so `calls.list`, `calls.make`, and `calls.retrieve` take an `agentId`; and workflows drop `prompt_config`.

  New: `agents.updateLiveStatus`, `agents.actions.enable`/`disable`, `conversations.send`, `conversations.setAiStatus`, `messages.retrieve`, and `workflows.clone`, plus typed workflow flows, guides, and FAQs.

## 0.1.1

### Patch Changes

- [#6](https://github.com/BimpeAI/bimpe-sdk/pull/6) [`03c579e`](https://github.com/BimpeAI/bimpe-sdk/commit/03c579e22347f6df0710d45150e0d3286ce63eab) Thanks [@Theshedman](https://github.com/Theshedman)! - Document installing prereleases from the `beta` dist-tag.

## 0.1.0

### Minor Changes

- [`bafa334`](https://github.com/BimpeAI/bimpe-sdk/commit/bafa33446f5d43a864032d132ed431f3ee599150) Thanks [@Theshedman](https://github.com/Theshedman)! - Initial release of the BimpeAI TypeScript SDK: typed coverage for Agents, Workflows, Conversations, and Messages, with built-in retries, idempotency, lazy pagination, and a typed error hierarchy. The Calls resource is wired but throws NotImplementedError until the upstream endpoint ships.

- [#1](https://github.com/BimpeAI/bimpe-sdk/pull/1) [`43f5948`](https://github.com/BimpeAI/bimpe-sdk/commit/43f594893b3a7c8c2cedeb4ff31ee37608e2b704) Thanks [@Theshedman](https://github.com/Theshedman)! - Add live conversation message streaming over Server-Sent Events: `conversations.messages.stream()` issues a ticket, opens the stream, yields each message, handles heartbeats, and auto-reconnects from the last seen message; `conversations.messages.streamTicket()` exposes the ticket step. Also export an `ErrorCode` union of the known envelope codes, including `too_many_requests`.

### Patch Changes

- [#1](https://github.com/BimpeAI/bimpe-sdk/pull/1) [`4136ee1`](https://github.com/BimpeAI/bimpe-sdk/commit/4136ee19d6bd89a61f4003f94329c0fd42bdcab2) Thanks [@Theshedman](https://github.com/Theshedman)! - Point the default base URL at `https://api.bimpe.ai`, so a client constructed without an explicit `baseUrl` reaches the live API.
