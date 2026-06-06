import type { Rule, RuleInput } from '../agents/types';

export type WorkflowVisibility = 'private' | 'public';
export type WorkflowScope = 'owned' | 'public';

export interface WorkflowSummary {
  readonly id: string;
  readonly name: string;
  readonly description: string | null;
  readonly category: string | null;
  readonly visibility: WorkflowVisibility;
  readonly is_owner: boolean;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface Workflow extends WorkflowSummary {
  readonly system_prompt: string | null;
  readonly rules: readonly Rule[];
  readonly flows: readonly Record<string, unknown>[];
  readonly tags: readonly string[];
  readonly prompt_config: Record<string, unknown>;
}

export interface CreateWorkflowBody {
  name: string;
  description?: string;
  category?: string;
  system_prompt?: string;
  rules?: RuleInput[];
  flows?: Record<string, unknown>[];
  tags?: string[];
  prompt_config?: Record<string, unknown>;
}

export type UpdateWorkflowBody = Partial<CreateWorkflowBody>;

export interface ListWorkflowsQuery {
  page?: number;
  limit?: number;
  search?: string;
  sort?: string;
  scope?: WorkflowScope;
}
