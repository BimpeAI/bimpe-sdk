from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict
from typing_extensions import NotRequired, TypedDict

from .workflows import Workflow

AgentPersona = Literal["professional", "friendly", "concise"]
AgentStatus = Literal["development", "live", "paused"]


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


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


class IntegrationSummary(_Model):
    id: str
    type: str
    name: str
    status: str
    is_connected: bool


class Integration(IntegrationSummary):
    config_fields: list[IntegrationConfigField] = []
    actions: list[IntegrationAction] = []


class ChannelSummary(_Model):
    id: str
    type: str
    name: str
    status: str
    is_connected: bool


Channel = ChannelSummary


class AgentAction(_Model):
    id: str
    integration_id: str
    integration_type: str
    integration_name: str
    name: str
    action_name: str
    description: str | None = None
    is_enabled: bool


class KnowledgeBaseSummary(_Model):
    id: str
    type: Literal["text", "url"]
    name: str
    description: str | None = None


class KnowledgeBase(KnowledgeBaseSummary):
    url: str | None = None
    content: str | None = None


class Agent(_Model):
    id: str
    name: str
    description: str
    workflow_id: str | None = None
    language: str | None = None
    persona: AgentPersona | None = None
    timezone: str | None = None
    logo: str | None = None
    business_name: str | None = None
    business_address: str | None = None
    business_email: str | None = None
    business_description: str | None = None
    test_channel_code: str | None = None
    status: AgentStatus | None = None
    status_reason: str | None = None
    escalation_email: str | None = None
    created_at: str
    updated_at: str


class AgentDetail(Agent):
    knowledge_bases: list[KnowledgeBaseSummary] = []
    integrations: list[IntegrationSummary] = []
    channels: list[ChannelSummary] = []


class AgentCreateResponse(Agent):
    workflow: Workflow | None = None


class CreateAgentBody(TypedDict):
    workflow_id: str
    name: str
    description: str
    language: NotRequired[str | None]
    persona: NotRequired[AgentPersona | None]
    timezone: NotRequired[str | None]
    logo: NotRequired[str | None]
    business_name: NotRequired[str | None]
    business_address: NotRequired[str | None]
    business_email: NotRequired[str | None]
    business_description: NotRequired[str | None]
    escalation_email: NotRequired[str | None]


class UpdateAgentBody(TypedDict, total=False):
    workflow_id: str
    name: str
    description: str
    language: str | None
    persona: AgentPersona | None
    timezone: str | None
    logo: str | None
    business_name: str | None
    business_address: str | None
    business_email: str | None
    business_description: str | None
    escalation_email: str | None


class UpdateLiveStatusBody(TypedDict):
    status: AgentStatus
    status_reason: NotRequired[str | None]


class BulkActionIdsBody(TypedDict):
    action_ids: list[str]


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
