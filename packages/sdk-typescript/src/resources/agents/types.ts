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

export interface Agent {
  readonly id: string;
  readonly name: string;
  readonly description: string | null;
  readonly system_prompt: string | null;
  readonly language: string | null;
  readonly persona: string | null;
  readonly agent_workflow_id: string | null;
  readonly rules: readonly Rule[] | null;
  readonly timezone: string | null;
  readonly logo: string | null;
  readonly business_name: string | null;
  readonly business_address: string | null;
  readonly business_email: string | null;
  readonly business_description: string | null;
  readonly test_channel_code: string | null;
  readonly status: string;
  readonly status_reason: string | null;
  readonly escalation_email: string | null;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface AgentDetail extends Agent {
  readonly integration: readonly AgentIntegration[];
  readonly channel: readonly AgentChannel[];
  readonly conversation_flow: readonly AgentConversationFlow[];
  readonly actions: readonly AgentActionSummary[];
  readonly knowledge_bases: readonly KnowledgeBaseSummary[];
}

export interface CreateAgentBody {
  name: string;
  description?: string | null;
  system_prompt?: string | null;
  language?: string | null;
  persona?: string | null;
  agent_workflow_id?: string | null;
  rules?: RuleInput[] | null;
  timezone?: string | null;
  logo?: string | null;
  business_name?: string | null;
  business_address?: string | null;
  business_email?: string | null;
  business_description?: string | null;
  escalation_email?: string | null;
}

export type UpdateAgentBody = Partial<CreateAgentBody>;

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

export interface AgentIntegration {
  readonly id: string;
  readonly type: string;
  readonly status: string;
  readonly is_connected: boolean;
  readonly config_fields: readonly IntegrationConfigField[];
  readonly actions: readonly IntegrationAction[];
}

export interface AgentChannel {
  readonly id: string;
  readonly type: string;
  readonly status: string;
  readonly is_connected: boolean;
}

export interface AgentConversationFlow {
  readonly name: string;
  readonly description: string | null;
  readonly category: string | null;
  readonly priority: number;
  readonly is_active: boolean;
}

export interface AgentActionSummary {
  readonly id: string;
  readonly integration_type: string;
  readonly integration_name: string;
  readonly name: string;
  readonly action_name: string;
  readonly description: string | null;
  readonly is_enabled: boolean;
}

export interface KnowledgeBaseSummary {
  readonly id: string;
  readonly type: 'text' | 'url';
  readonly name: string;
  readonly description: string | null;
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
