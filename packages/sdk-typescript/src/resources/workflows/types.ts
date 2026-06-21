import type { Rule, RuleInput } from '../agents/types';

export type WorkflowVisibility = 'private' | 'public';
export type WorkflowScope = 'owned' | 'public' | 'accessible';

export interface FlowTriggerKeyword {
  keyword: string;
  weight?: 'high' | 'medium' | 'low';
}

export interface FlowStep {
  type: string;
  content?: string;
  action?: string;
  followup?: string;
}

export interface Flow {
  name: string;
  description?: string | null;
  category?: string | null;
  priority?: number;
  is_active?: boolean;
  trigger_keywords?: FlowTriggerKeyword[];
  conversation_steps?: FlowStep[];
}

export interface WorkflowGuide {
  youtubeUrl?: string;
  steps: string[];
}

export interface WorkflowFaq {
  question: string;
  answer: string;
}

export interface Workflow {
  readonly id: string;
  readonly name: string;
  readonly description: string | null;
  readonly category: string | null;
  readonly visibility: WorkflowVisibility;
  readonly is_owner: boolean;
  readonly system_prompt: string | null;
  readonly rules: readonly Rule[];
  readonly flows: readonly Flow[];
  readonly tags: readonly string[] | null;
  readonly integrations: readonly string[] | null;
  readonly channels: readonly string[] | null;
  readonly actions: readonly string[] | null;
  readonly guide: WorkflowGuide | null;
  readonly faq: readonly WorkflowFaq[] | null;
  readonly setup_steps: readonly (string | Record<string, unknown>)[];
  readonly setup_time: number | null;
  readonly video_url: string | null;
  readonly created_at: string;
  readonly updated_at: string;
}

export type WorkflowDetail = Workflow;

/** @deprecated The list endpoint now returns the full `Workflow`. Use `Workflow` instead. */
export type WorkflowSummary = Workflow;

export interface CreateWorkflowBody {
  name: string;
  system_prompt: string;
  description?: string;
  category?: string;
  rules?: RuleInput[];
  flows?: Flow[];
  tags?: string[];
  integrations?: string[];
  channels?: string[];
  actions?: string[];
  guide?: WorkflowGuide;
  faq?: WorkflowFaq[];
  setup_steps?: (string | Record<string, unknown>)[];
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
