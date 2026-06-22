import type { WorkflowDetail } from '../workflows/types';

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
