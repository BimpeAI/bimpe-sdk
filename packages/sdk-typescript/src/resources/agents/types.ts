import type { Workflow } from '../workflows/types';

export interface Rule {
  readonly id: string;
  readonly name: string;
  readonly trigger: string;
  readonly condition: string | null;
  readonly response: string;
  readonly action: string | null;
  readonly enabled: boolean;
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
export type AgentStatus = 'development' | 'live' | 'paused';

export interface Agent {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly workflow_id: string | null;
  readonly language: string | null;
  readonly persona: AgentPersona | null;
  readonly timezone: string | null;
  readonly logo: string | null;
  readonly business_name: string | null;
  readonly business_address: string | null;
  readonly business_email: string | null;
  readonly business_description: string | null;
  readonly test_channel_code: string | null;
  readonly status: AgentStatus | null;
  readonly status_reason: string | null;
  readonly escalation_email: string | null;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface AgentIntegrationSummary {
  readonly id: string;
  readonly type: string;
  readonly name: string;
  readonly status: string;
  readonly is_connected: boolean;
}

export interface AgentChannelSummary {
  readonly id: string;
  readonly type: string;
  readonly name: string;
  readonly status: string;
  readonly is_connected: boolean;
}

export interface KnowledgeBaseSummary {
  readonly id: string;
  readonly type: 'text' | 'url';
  readonly name: string;
  readonly description: string | null;
}

export interface AgentDetail extends Agent {
  readonly knowledge_bases: readonly KnowledgeBaseSummary[];
  readonly integrations: readonly AgentIntegrationSummary[];
  readonly channels: readonly AgentChannelSummary[];
}

export interface AgentCreateResponse extends Agent {
  readonly workflow?: Workflow | null;
}

export interface CreateAgentBody {
  workflow_id: string;
  name: string;
  description: string;
  language?: string | null;
  persona?: AgentPersona | null;
  timezone?: string | null;
  logo?: string | null;
  business_name?: string | null;
  business_address?: string | null;
  business_email?: string | null;
  business_description?: string | null;
  escalation_email?: string | null;
}

export type UpdateAgentBody = Partial<CreateAgentBody>;

export type UpdateLiveStatusBody = {
  status: AgentStatus;
  status_reason?: string | null;
};

export interface BulkActionIdsBody {
  action_ids: string[];
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

export interface AgentIntegration extends AgentIntegrationSummary {
  readonly config_fields: readonly IntegrationConfigField[];
  readonly actions: readonly IntegrationAction[];
}

export interface AgentChannel extends AgentChannelSummary {}

export interface AgentActionSummary {
  readonly id: string;
  readonly integration_id: string;
  readonly integration_type: string;
  readonly integration_name: string;
  readonly name: string;
  readonly action_name: string;
  readonly description: string | null;
  readonly is_enabled: boolean;
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

export interface KnowledgeBaseItem extends KnowledgeBaseSummary {
  readonly url?: string | null;
  readonly content?: string | null;
}
