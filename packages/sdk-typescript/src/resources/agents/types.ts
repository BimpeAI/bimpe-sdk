import type { WorkflowDetail } from '../workflows/types';

export interface Rule {
  // Only `id` is guaranteed; a workflow may carry a partially-populated rule.
  readonly id: string;
  readonly name: string | null;
  readonly trigger: string | null;
  readonly condition: string | null;
  readonly response: string | null;
  readonly action: string | null;
  readonly enabled: boolean | null;
}

export interface RuleInput {
  id: string;
  name: string;
  trigger: string;
  condition?: string | null;
  response: string;
  action?: string | null;
  enabled: boolean;
}

export type AgentPersona = 'professional' | 'friendly' | 'concise';
export type AgentLiveStatusValue = 'development' | 'live' | 'paused';

export interface Agent {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly language: string | null;
  readonly persona: AgentPersona | null;
  readonly workflow_id: string | null;
  readonly timezone: string | null;
  readonly logo: string | null;
  readonly business_name: string | null;
  readonly business_address: string | null;
  readonly business_email: string | null;
  readonly business_description: string | null;
  readonly test_channel_code: string | null;
  readonly status: AgentLiveStatusValue | null;
  readonly status_reason: string | null;
  readonly escalation_email: string | null;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface AgentDetail extends Agent {
  readonly knowledge_bases: readonly KnowledgeBaseSummary[];
  readonly integrations: readonly IntegrationSummary[];
  readonly channels: readonly AgentChannel[];
}

export interface AgentCreateResponse extends Agent {
  readonly workflow: WorkflowDetail | null;
}

export interface CreateAgentBody {
  workflow_id: string;
  name: string;
  description: string;
  language?: string;
  persona?: AgentPersona;
  timezone?: string;
  logo?: string;
  business_name?: string;
  business_address?: string;
  business_email?: string;
  business_description?: string;
  escalation_email?: string;
}

export type UpdateAgentBody = Partial<CreateAgentBody>;

export interface UpdateLiveStatusBody {
  status: AgentLiveStatusValue;
  status_reason?: string;
}

export interface AgentLiveStatus {
  readonly status: string;
  readonly status_reason: string | null;
}

export interface IntegrationConfigField {
  readonly key: string;
  readonly label: string;
  readonly type: string;
  readonly required: boolean;
}

export interface IntegrationAction {
  readonly action_name: string;
  readonly name: string;
  readonly description: string | null;
  readonly category: string;
  readonly is_enabled: boolean;
  readonly require_human_approval: boolean;
}

export interface IntegrationSummary {
  readonly id: string;
  readonly type: string;
  readonly name: string;
  readonly status: string;
  readonly is_connected: boolean;
}

export interface AgentIntegration extends IntegrationSummary {
  readonly config_fields: readonly IntegrationConfigField[];
  readonly actions: readonly IntegrationAction[];
}

export interface AgentChannel {
  readonly id: string;
  readonly type: string;
  readonly name: string;
  readonly status: string;
  readonly is_connected: boolean;
}

export interface AgentAction {
  readonly id: string;
  readonly integration_id: string;
  readonly integration_type: string;
  readonly integration_name: string;
  readonly name: string;
  readonly action_name: string;
  readonly description: string | null;
  readonly is_enabled: boolean;
}

export interface BulkActionIdsBody {
  action_ids: string[];
}

export interface BulkActionUpdate {
  readonly updated_count: number;
}

export interface KnowledgeBaseSummary {
  readonly id: string;
  readonly type: 'text' | 'url';
  readonly name: string;
  readonly description: string | null;
}

export interface KnowledgeBaseItem extends KnowledgeBaseSummary {
  readonly url: string | null;
  readonly content: string | null;
}

export interface CreateKnowledgeBaseTextBody {
  type: 'text';
  name: string;
  description?: string | null;
  content: string;
}

export interface CreateKnowledgeBaseUrlBody {
  type: 'url';
  name: string;
  description?: string | null;
  url: string;
}

export type CreateKnowledgeBaseBody = CreateKnowledgeBaseTextBody | CreateKnowledgeBaseUrlBody;

export interface UpdateKnowledgeBaseBody {
  name?: string;
  description?: string | null;
  content?: string | null;
  url?: string | null;
}

export type BimpeaiIntegrationType =
  | 'bumpa'
  | 'google_calendar'
  | 'google_sheets'
  | 'paystack'
  | 'stripe';

export interface BimpeaiIntegration {
  readonly id: string | null;
  readonly type: BimpeaiIntegrationType;
  readonly name: string;
  readonly status: string;
  readonly is_connected: boolean;
}

export interface BimpeaiConfigureBody {
  type: BimpeaiIntegrationType;
  token?: string;
  public_key?: string;
  secret_key?: string;
  currency?: string;
}

export interface OnboardingUrl {
  readonly onboarding_url: string;
}

export interface DeploymentWhatsAppChannel {
  readonly is_enabled: boolean;
  readonly start_message: string;
  readonly phone_number?: string | null;
  readonly url?: string | null;
}

export interface DeploymentInstagramChannel {
  readonly is_enabled: boolean;
  readonly start_message: string;
  readonly username?: string | null;
  readonly url?: string | null;
}

export interface DeploymentMessengerChannel {
  readonly is_enabled: boolean;
  readonly start_message: string;
  readonly page?: string | null;
  readonly url?: string | null;
}

export interface DeploymentTelephonyChannel {
  readonly is_enabled: boolean;
}

export interface DeploymentChannels {
  readonly whatsapp: DeploymentWhatsAppChannel;
  readonly instagram: DeploymentInstagramChannel;
  readonly messenger: DeploymentMessengerChannel;
  readonly telephony: DeploymentTelephonyChannel;
}

export interface AgentTestCode {
  readonly code: string;
  readonly channels: DeploymentChannels;
}

export type IntegrationAuthType = 'none' | 'bearer' | 'basic' | 'api_key' | 'custom';

export interface IntegrationAuthConfig {
  token?: string;
  api_key?: string;
  header_name?: string;
  username?: string;
  password?: string;
}

export interface IntegrationTool {
  readonly id: string;
  readonly action_name: string;
  readonly name: string;
  readonly description: string | null;
  readonly category: string;
  readonly is_enabled: boolean;
}

export interface CustomApiConfig {
  readonly name: string;
  readonly base_url?: string;
  readonly auth_type: string;
}

export interface CustomApiIntegration {
  readonly id: string;
  readonly config: CustomApiConfig;
}

export interface CustomApiConfigureBody {
  name: string;
  description?: string;
  base_url?: string;
  auth_type?: IntegrationAuthType;
  auth_config?: IntegrationAuthConfig;
  test_endpoint?: string;
}

export type ParameterType = 'string' | 'number' | 'integer' | 'boolean' | 'array' | 'object';

export interface ParameterDefinition {
  name: string;
  type: ParameterType;
  description: string;
  required?: boolean;
  items?: ParameterDefinition;
  properties?: Record<string, unknown>;
}

export type ToolHttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

export interface ToolResponseMapping {
  path?: string;
  success_message?: string;
  error_message?: string;
}

export interface CustomApiCreateToolBody {
  name: string;
  http_method: ToolHttpMethod;
  url_template: string;
  description?: string;
  url_params?: ParameterDefinition[];
  body_params?: ParameterDefinition[];
  headers_template?: Record<string, unknown>;
  body_template?: Record<string, unknown>;
  auth_type?: IntegrationAuthType;
  auth_config?: Record<string, unknown>;
  response_mapping?: ToolResponseMapping;
  category?: string;
  require_human_approval?: boolean;
  timeout?: number;
}

export type McpServerTransport = 'http_sse' | 'streamable_http';

export interface McpServerConfig {
  readonly name: string;
  readonly server_url: string;
  readonly transport: McpServerTransport;
  readonly auth_type: string;
}

export interface McpServerIntegration {
  readonly id: string;
  readonly config: McpServerConfig;
}

export interface McpServerConfigureBody {
  name: string;
  server_url: string;
  transport?: McpServerTransport;
  auth_type?: IntegrationAuthType;
  auth_config?: IntegrationAuthConfig;
}

export interface McpServerTestResult {
  readonly success: boolean;
  readonly message: string;
  readonly error?: string;
  readonly tools_count?: number;
}

export interface McpServerDiscoverResult {
  readonly discovered: number;
  readonly created: number;
  readonly updated: number;
  readonly disabled: number;
}

export interface PipedreamConfigureBody {
  app_slug: string;
  app_name?: string;
  app_icon?: string;
}

export interface PipedreamIntegrationConfig {
  readonly app_slug: string;
  readonly app_name?: string;
  readonly app_icon?: string | null;
  readonly server_url: string;
}

export interface PipedreamIntegration {
  readonly id: string;
  readonly channel_type: string;
  readonly config: PipedreamIntegrationConfig;
}
