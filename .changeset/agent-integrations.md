---
'@bimpeai/sdk': minor
---

Add the agent integrations subsystem and the test-code endpoint. `agents.getTestCode` returns the agent's test code and the per-channel deep links used to start a test conversation. `agents.integrations` becomes writable through four connector families, each with `list`, `configure`, and `disconnect`: `bimpeai` for first-party connectors (Google Calendar, Stripe, Paystack, Google Sheets, Bumpa), `customApi` for custom HTTP APIs with a nested `tools` sub-resource, `mcpServer` for MCP servers with `discover`, `test`, and a `tools` listing, and `pipedream` for OAuth onboarding. The existing read-only `integrations.list` is unchanged.
