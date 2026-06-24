from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict
from typing_extensions import NotRequired, TypedDict

if TYPE_CHECKING:
    from .workflows import WorkflowDetail

AgentPersona = Literal["professional", "friendly", "concise"]
AgentLiveStatusValue = Literal["development", "live", "paused"]


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


class IntegrationSummary(_Model):
    id: str
    type: str
    name: str
    status: str
    is_connected: bool


class AgentIntegration(IntegrationSummary):
    config_fields: list[IntegrationConfigField] = []
    actions: list[IntegrationAction] = []


class AgentChannel(_Model):
    id: str
    type: str
    name: str
    status: str
    is_connected: bool


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


class KnowledgeBaseItem(KnowledgeBaseSummary):
    url: str | None = None
    content: str | None = None


class Agent(_Model):
    id: str
    name: str
    description: str
    language: str | None = None
    persona: AgentPersona | None = None
    workflow_id: str | None = None
    timezone: str | None = None
    logo: str | None = None
    business_name: str | None = None
    business_address: str | None = None
    business_email: str | None = None
    business_description: str | None = None
    test_channel_code: str | None = None
    status: AgentLiveStatusValue | None = None
    status_reason: str | None = None
    escalation_email: str | None = None
    created_at: str
    updated_at: str


class AgentDetail(Agent):
    knowledge_bases: list[KnowledgeBaseSummary] = []
    integrations: list[IntegrationSummary] = []
    channels: list[AgentChannel] = []


class AgentCreateResponse(Agent):
    workflow: WorkflowDetail | None = None


class AgentLiveStatus(_Model):
    status: str
    status_reason: str | None = None


class BulkActionUpdate(_Model):
    updated_count: int


class RuleInput(TypedDict):
    id: str
    name: str
    trigger: str
    response: str
    enabled: bool
    condition: NotRequired[str | None]
    action: NotRequired[str | None]


class CreateAgentBody(TypedDict):
    workflow_id: str
    name: str
    description: str
    language: NotRequired[str]
    persona: NotRequired[AgentPersona]
    timezone: NotRequired[str]
    logo: NotRequired[str]
    business_name: NotRequired[str]
    business_address: NotRequired[str]
    business_email: NotRequired[str]
    business_description: NotRequired[str]
    escalation_email: NotRequired[str]


class UpdateAgentBody(TypedDict, total=False):
    workflow_id: str
    name: str
    description: str
    language: str
    persona: AgentPersona
    timezone: str
    logo: str
    business_name: str
    business_address: str
    business_email: str
    business_description: str
    escalation_email: str


class UpdateLiveStatusBody(TypedDict):
    status: AgentLiveStatusValue
    status_reason: NotRequired[str]


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


BimpeaiIntegrationType = Literal["bumpa", "google_calendar", "google_sheets", "paystack", "stripe"]


class BimpeaiIntegration(_Model):
    id: str | None = None
    type: BimpeaiIntegrationType
    name: str
    status: str
    is_connected: bool


class OnboardingUrl(_Model):
    onboarding_url: str


class DeploymentWhatsAppChannel(_Model):
    is_enabled: bool
    start_message: str
    phone_number: str | None = None
    url: str | None = None


class DeploymentInstagramChannel(_Model):
    is_enabled: bool
    start_message: str
    username: str | None = None
    url: str | None = None


class DeploymentMessengerChannel(_Model):
    is_enabled: bool
    start_message: str
    page: str | None = None
    url: str | None = None


class DeploymentTelephonyChannel(_Model):
    is_enabled: bool


class DeploymentChannels(_Model):
    whatsapp: DeploymentWhatsAppChannel
    instagram: DeploymentInstagramChannel
    messenger: DeploymentMessengerChannel
    telephony: DeploymentTelephonyChannel


class AgentTestCode(_Model):
    code: str
    channels: DeploymentChannels


class BimpeaiConfigureBody(TypedDict):
    type: BimpeaiIntegrationType
    token: NotRequired[str]
    public_key: NotRequired[str]
    secret_key: NotRequired[str]
    currency: NotRequired[str]


IntegrationAuthType = Literal["none", "bearer", "basic", "api_key", "custom"]
ParameterType = Literal["string", "number", "integer", "boolean", "array", "object"]
ToolHttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
McpServerTransport = Literal["http_sse", "streamable_http"]


class IntegrationTool(_Model):
    id: str
    action_name: str
    name: str
    description: str | None = None
    category: str
    is_enabled: bool


class CustomApiConfig(_Model):
    name: str
    base_url: str | None = None
    auth_type: str


class CustomApiIntegration(_Model):
    id: str
    config: CustomApiConfig


class McpServerConfig(_Model):
    name: str
    server_url: str
    transport: McpServerTransport
    auth_type: str


class McpServerIntegration(_Model):
    id: str
    config: McpServerConfig


class McpServerTestResult(_Model):
    success: bool
    message: str
    error: str | None = None
    tools_count: int | None = None


class McpServerDiscoverResult(_Model):
    discovered: int
    created: int
    updated: int
    disabled: int


class PipedreamIntegrationConfig(_Model):
    app_slug: str
    app_name: str | None = None
    app_icon: str | None = None
    server_url: str


class PipedreamIntegration(_Model):
    id: str
    channel_type: str
    config: PipedreamIntegrationConfig


class IntegrationAuthConfig(TypedDict, total=False):
    token: str
    api_key: str
    header_name: str
    username: str
    password: str


class ToolResponseMapping(TypedDict, total=False):
    path: str
    success_message: str
    error_message: str


class CustomApiConfigureBody(TypedDict):
    name: str
    description: NotRequired[str]
    base_url: NotRequired[str]
    auth_type: NotRequired[IntegrationAuthType]
    auth_config: NotRequired[IntegrationAuthConfig]
    test_endpoint: NotRequired[str]


class ParameterDefinition(TypedDict):
    name: str
    type: ParameterType
    description: str
    required: NotRequired[bool]
    items: NotRequired[ParameterDefinition]
    properties: NotRequired[dict[str, Any]]


class CustomApiCreateToolBody(TypedDict):
    name: str
    http_method: ToolHttpMethod
    url_template: str
    description: NotRequired[str]
    url_params: NotRequired[list[ParameterDefinition]]
    body_params: NotRequired[list[ParameterDefinition]]
    headers_template: NotRequired[dict[str, Any]]
    body_template: NotRequired[dict[str, Any]]
    auth_type: NotRequired[IntegrationAuthType]
    auth_config: NotRequired[dict[str, Any]]
    response_mapping: NotRequired[ToolResponseMapping]
    category: NotRequired[str]
    require_human_approval: NotRequired[bool]
    timeout: NotRequired[int]


class McpServerConfigureBody(TypedDict):
    name: str
    server_url: str
    transport: NotRequired[McpServerTransport]
    auth_type: NotRequired[IntegrationAuthType]
    auth_config: NotRequired[IntegrationAuthConfig]


class PipedreamConfigureBody(TypedDict):
    app_slug: str
    app_name: NotRequired[str]
    app_icon: NotRequired[str]
