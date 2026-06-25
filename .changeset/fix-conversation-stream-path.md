---
'@bimpeai/sdk': patch
---

Fix the conversation message stream path. The SSE endpoint moved from `.../conversations/{id}/messages/stream` to `.../conversations/{id}/stream`; `conversations.messages.stream` now targets the new path, so streaming connects instead of returning a 404. This mirrors the same one-line path fix in the Python SDK.
