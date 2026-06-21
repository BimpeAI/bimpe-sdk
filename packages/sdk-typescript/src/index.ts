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
  AgentActionSummary,
  AgentChannel,
  AgentChannelSummary,
  AgentCreateResponse,
  AgentDetail,
  AgentIntegration,
  AgentIntegrationSummary,
  AgentPersona,
  AgentStatus,
  BulkActionIdsBody,
  CreateAgentBody,
  CreateKnowledgeBaseBody,
  CreateKnowledgeBaseTextBody,
  CreateKnowledgeBaseUrlBody,
  IntegrationAction,
  IntegrationConfigField,
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
  ListWorkflowsQuery,
  UpdateWorkflowBody,
  Workflow,
  WorkflowFaqItem,
  WorkflowGuide,
  WorkflowScope,
  WorkflowSummary,
  WorkflowVisibility,
} from './resources/workflows';
export { Calls } from './resources/calls';
export type {
  Call,
  CallsNotImplementedResponse,
  MakeCallBody,
  QueueCallBody,
} from './resources/calls';
export { Conversations, Messages } from './resources/conversations';
export type {
  Conversation,
  ConversationChannel,
  ConversationListItem,
  CreateOrSendByChannelBody,
  CreateOrSendChannelType,
  CreateOrSendExistingBody,
  CreateOrSendMessageBody,
  CreateOrSendMessageResponse,
  ListConversationsQuery,
  ListMessagesQuery,
  Message,
  MessageAttachment,
  MessageRole,
  SendMessageBody,
  SendToConversationBody,
  StreamHeartbeatEvent,
  StreamMessageEvent,
  StreamMessageRole,
  StreamOptions,
  StreamTicket,
  UpdateAiStatusBody,
  UpdateAiStatusResponse,
} from './resources/conversations';
export { VERSION } from './version';
