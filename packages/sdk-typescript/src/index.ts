export { BimpeAI } from './client';
export type { BimpeAIConfig } from './client';
export {
  ApiError,
  AuthenticationError,
  BadRequestError,
  BimpeAIError,
  ConflictError,
  ConnectionError,
  ConnectionTimeoutError,
  InternalServerError,
  NotFoundError,
  NotImplementedError,
  PermissionDeniedError,
  RateLimitError,
  UserError,
  ValidationError,
} from './core/errors';
export type { FieldError } from './core/errors';
export { Page } from './core/pagination';
export type { ApiResponse, ListQuery, PaginationMeta, RequestOptions } from './core/types';
export {
  AgentActions,
  AgentChannels,
  AgentConversationFlows,
  AgentIntegrations,
  Agents,
} from './resources/agents';
export type {
  Agent,
  AgentActionSummary,
  AgentChannel,
  AgentConversationFlow,
  AgentDetail,
  AgentIntegration,
  CreateAgentBody,
  CreateKnowledgeBaseBody,
  CreateKnowledgeBaseTextBody,
  CreateKnowledgeBaseUrlBody,
  IntegrationAction,
  IntegrationConfigField,
  KnowledgeBaseSummary,
  Rule,
  RuleInput,
  UpdateAgentBody,
  UpdateKnowledgeBaseBody,
} from './resources/agents';
export { VERSION } from './version';
