---
"@bimpeai/sdk": minor
---

Align the SDK with Console API v1.

Breaking: `agents.create` now takes `workflow_id` (and `system_prompt`/`rules` are gone), `persona` is an enum, and it returns an `AgentCreateResponse` carrying the nested workflow; the `Agent` read type renames `agent_workflow_id` to `workflow_id` and drops `system_prompt`/`rules`, and `AgentDetail` is reshaped (nested `knowledge_bases`/`integrations`/`channels`, with `conversation_flow` and `actions` removed); `agents.conversationFlows` is removed; the knowledge base methods return the fuller `KnowledgeBaseItem`; `conversations.retrieve` returns a `ConversationDetail` distinct from the list item; sending a message no longer accepts `attachments` (they still appear on message responses); the conversation channel set drops `messenger` and `instagram` and adds `telephony` and `test_webchat`; calls are now agent-scoped and live, so `calls.list`, `calls.make`, and `calls.retrieve` take an `agentId`; and workflows drop `prompt_config`.

New: `agents.updateLiveStatus`, `agents.actions.enable`/`disable`, `conversations.send`, `conversations.setAiStatus`, `messages.retrieve`, and `workflows.clone`, plus typed workflow flows, guides, and FAQs.
