---
'@bimpeai/sdk': minor
---

Correct two response types that did not match the shapes the server actually returns. `phoneNumbers.requests.list` now returns a dedicated `PhoneNumberRequest` (a provisioning request has no `e164` until it is fulfilled) instead of `PhoneNumber`, and a workflow's `setup_steps` is now typed `unknown[]` to match the server. A workflow's `Rule` fields other than `id` are now optional as well, so a partially-populated rule (for example one created without `enabled`) can no longer fail validation of the whole workflow. This mirrors the parallel fix in the Python SDK, where the stricter pydantic models were raising `ValidationError` on otherwise-valid `phoneNumbers.requests.list` and `workflows.list` responses.

It also adds `agents.delete(agentId)` for the new `DELETE /agents/{id}` endpoint, which the SDKs did not previously expose.
