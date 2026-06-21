import type { Rule, RuleInput } from '../agents/types';

export type WorkflowVisibility = 'private' | 'public';
export type WorkflowScope = 'accessible' | 'owned' | 'public';

export interface WorkflowGuide {
  readonly youtubeUrl?: string;
  readonly steps: readonly string[];
}

export interface WorkflowFaqItem {
  readonly question: string;
  readonly answer: string;
}

export interface Workflow {
  readonly id: string;
  readonly name: string;
  readonly description: string | null;
  readonly category: string | null;
  readonly visibility: WorkflowVisibility;
  readonly is_owner: boolean;
  readonly created_at: string;
  readonly updated_at: string;
  readonly system_prompt: string | null;
  readonly rules: readonly Rule[];
  readonly flows: readonly Record<string, unknown>[];
  readonly tags: readonly string[];
  readonly integrations: readonly string[];
  readonly channels: readonly string[];
  readonly actions: readonly string[];
  readonly guide: WorkflowGuide | null;
  readonly faq: readonly WorkflowFaqItem[];
  readonly setup_steps: readonly unknown[];
  readonly setup_time: number | null;
  readonly video_url: string | null;
}

/** @deprecated List items use the full {@link Workflow} shape. */
export type WorkflowSummary = Workflow;

export interface CreateWorkflowBody {
  name: string;
  system_prompt: string;
  description?: string;
  category?: string;
  rules?: RuleInput[];
  flows?: Record<string, unknown>[];
  tags?: string[];
  integrations?: string[];
  channels?: string[];
  actions?: string[];
  guide?: WorkflowGuide;
  faq?: WorkflowFaqItem[];
  setup_steps?: unknown[];
  setup_time?: number;
  video_url?: string;
}

export type UpdateWorkflowBody = Partial<CreateWorkflowBody>;

export interface CloneWorkflowBody {
  source_workflow_id: string;
}

export interface ListWorkflowsQuery {
  page?: number;
  limit?: number;
  search?: string;
  sort?: string;
  scope?: WorkflowScope;
}
