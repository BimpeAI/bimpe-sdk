---
'@bimpeai/sdk': minor
---

Add a team-scoped `phoneNumbers` resource. `phoneNumbers.list`, `retrieve`, and `update` manage number assignments (linking a number to an agent and labelling it), and a nested `phoneNumbers.requests.list`/`create` lists and submits provisioning requests. A number linked to an agent is the live telephony channel that `calls.make({ is_test_call: false })` dials out over.
