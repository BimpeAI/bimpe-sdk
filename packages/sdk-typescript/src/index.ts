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
export type { ErrorCode, FieldError } from './core/errors';
export { Page, PagePromise } from './core/pagination';
export type { ApiResponse, ListQuery, PaginationMeta, RequestOptions } from './core/types';
export {
  AgentActions,
  AgentChannels,
  AgentIntegrations,
  AgentKnowledgeBases,
  Agents,
} from './resources/agents';
export type {
  Agent,
  AgentAction,
  AgentChannel,
  AgentCreateResponse,
  AgentDetail,
  AgentIntegration,
  AgentLiveStatus,
  AgentLiveStatusValue,
  AgentPersona,
  BulkActionIdsBody,
  BulkActionUpdate,
  CreateAgentBody,
  CreateKnowledgeBaseBody,
  CreateKnowledgeBaseTextBody,
  CreateKnowledgeBaseUrlBody,
  IntegrationAction,
  IntegrationConfigField,
  IntegrationSummary,
  KnowledgeBaseItem,
  KnowledgeBaseSummary,
  Rule,
  RuleInput,
  UpdateAgentBody,
  UpdateKnowledgeBaseBody,
  UpdateLiveStatusBody,
} from './resources/agents';
export { Workflows } from './resources/workflows';
export type {
  CloneWorkflowBody,
  CreateWorkflowBody,
  Flow,
  FlowStep,
  FlowTriggerKeyword,
  ListWorkflowsQuery,
  UpdateWorkflowBody,
  Workflow,
  WorkflowDetail,
  WorkflowFaq,
  WorkflowGuide,
  WorkflowScope,
  WorkflowSummary,
  WorkflowVisibility,
} from './resources/workflows';
export { Conversations, Messages } from './resources/conversations';
export type {
  Conversation,
  ConversationAiStatus,
  ConversationChannel,
  ConversationDetail,
  CreateConversationMessageBody,
  ListConversationsQuery,
  ListMessagesQuery,
  Message,
  MessageAttachment,
  MessageRole,
  SendMessageBody,
  SetAiStatusBody,
  StreamHeartbeatEvent,
  StreamMessageEvent,
  StreamMessageRole,
  StreamOptions,
  StreamTicket,
} from './resources/conversations';
export { Calls } from './resources/calls';
export type {
  Call,
  CallDetail,
  CallMessage,
  CallMessageAttachment,
  CallStatus,
  ListCallsQuery,
  MakeCallBody,
  MakeCallResult,
  MakeCallStatus,
} from './resources/calls';
export { VERSION } from './version';
