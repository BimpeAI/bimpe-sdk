---
'@bimpeai/sdk': minor
---

Add live conversation message streaming over Server-Sent Events: `conversations.messages.stream()` issues a ticket, opens the stream, yields each message, handles heartbeats, and auto-reconnects from the last seen message; `conversations.messages.streamTicket()` exposes the ticket step. Also export an `ErrorCode` union of the known envelope codes, including `too_many_requests`.
