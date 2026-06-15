from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict
from typing_extensions import NotRequired, TypedDict


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


class Rule(_Model):
    id: str
    name: str
    trigger: str
    condition: str | None = None
    response: str
    action: str | None = None
    enabled: bool


class IntegrationConfigField(_Model):
    key: str
    label: str
    type: str
    required: bool


class IntegrationAction(_Model):
    action_name: str
    name: str
    description: str | None = None
    category: str
    is_enabled: bool
    require_human_approval: bool


class Integration(_Model):
    id: str
    type: str
    status: str
    is_connected: bool
    config_fields: list[IntegrationConfigField] = []
    actions: list[IntegrationAction] = []


class Channel(_Model):
    id: str
    type: str
    status: str
    is_connected: bool


class ConversationFlow(_Model):
    name: str
    description: str | None = None
    category: str | None = None
    priority: int
    is_active: bool


class AgentAction(_Model):
    id: str
    integration_type: str
    integration_name: str
    name: str
    action_name: str
    description: str | None = None
    is_enabled: bool


class KnowledgeBase(_Model):
    id: str
    type: Literal["text", "url"]
    name: str
    description: str | None = None


class Agent(_Model):
    id: str
    name: str
    description: str | None = None
    system_prompt: str | None = None
    language: str | None = None
    persona: str | None = None
    agent_workflow_id: str | None = None
    rules: list[Rule] | None = None
    timezone: str | None = None
    logo: str | None = None
    business_name: str | None = None
    business_address: str | None = None
    business_email: str | None = None
    business_description: str | None = None
    test_channel_code: str | None = None
    status: str
    status_reason: str | None = None
    escalation_email: str | None = None
    created_at: str
    updated_at: str


class AgentDetail(Agent):
    integration: list[Integration] = []
    channel: list[Channel] = []
    conversation_flow: list[ConversationFlow] = []
    actions: list[AgentAction] = []
    knowledge_bases: list[KnowledgeBase] = []


class RuleInput(TypedDict):
    id: str
    name: str
    trigger: str
    response: str
    enabled: bool
    condition: NotRequired[str | None]
    action: NotRequired[str | None]


class CreateAgentBody(TypedDict):
    name: str
    description: NotRequired[str | None]
    system_prompt: NotRequired[str | None]
    language: NotRequired[str | None]
    persona: NotRequired[str | None]
    agent_workflow_id: NotRequired[str | None]
    rules: NotRequired[list[RuleInput] | None]
    timezone: NotRequired[str | None]
    logo: NotRequired[str | None]
    business_name: NotRequired[str | None]
    business_address: NotRequired[str | None]
    business_email: NotRequired[str | None]
    business_description: NotRequired[str | None]
    escalation_email: NotRequired[str | None]


class UpdateAgentBody(TypedDict, total=False):
    name: str
    description: str | None
    system_prompt: str | None
    language: str | None
    persona: str | None
    agent_workflow_id: str | None
    rules: list[RuleInput] | None
    timezone: str | None
    logo: str | None
    business_name: str | None
    business_address: str | None
    business_email: str | None
    business_description: str | None
    escalation_email: str | None


class CreateKnowledgeBaseTextBody(TypedDict):
    type: Literal["text"]
    name: str
    content: str
    description: NotRequired[str | None]


class CreateKnowledgeBaseUrlBody(TypedDict):
    type: Literal["url"]
    name: str
    url: str
    description: NotRequired[str | None]


CreateKnowledgeBaseBody = CreateKnowledgeBaseTextBody | CreateKnowledgeBaseUrlBody


class UpdateKnowledgeBaseBody(TypedDict, total=False):
    name: str
    description: str | None
    content: str | None
    url: str | None
