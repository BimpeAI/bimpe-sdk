import { Page, PagePromise } from '../../core/pagination';
import type { RequestOptions, Transport } from '../../core/types';
import { Messages } from './messages';
import type {
  Conversation,
  ConversationListItem,
  CreateOrSendMessageBody,
  CreateOrSendMessageResponse,
  ListConversationsQuery,
  UpdateAiStatusBody,
  UpdateAiStatusResponse,
} from './types';

type Client = Transport;

export class Conversations {
  readonly messages: Messages;

  constructor(private readonly client: Client) {
    this.messages = new Messages(client);
  }

  list(agentId: string, query: ListConversationsQuery = {}): PagePromise<ConversationListItem> {
    return new PagePromise(() => this.fetchPage(agentId, query.page ?? 1, query));
  }

  async retrieve(agentId: string, conversationId: string): Promise<Conversation> {
    const res = await this.client.request<Conversation>({
      method: 'GET',
      path: `/agents/${agentId}/conversations/${conversationId}`,
    });
    return res.data;
  }

  async createOrSendMessage(
    agentId: string,
    body: CreateOrSendMessageBody,
    options: RequestOptions = {},
  ): Promise<CreateOrSendMessageResponse> {
    const res = await this.client.request<CreateOrSendMessageResponse>({
      method: 'POST',
      path: `/agents/${agentId}/conversations/messages`,
      body,
      ...options,
    });
    return res.data;
  }

  async updateAiStatus(
    agentId: string,
    conversationId: string,
    body: UpdateAiStatusBody,
  ): Promise<UpdateAiStatusResponse> {
    const res = await this.client.request<UpdateAiStatusResponse>({
      method: 'PATCH',
      path: `/agents/${agentId}/conversations/${conversationId}/ai-status`,
      body,
    });
    return res.data;
  }

  private async fetchPage(
    agentId: string,
    page: number,
    query: ListConversationsQuery,
  ): Promise<Page<ConversationListItem>> {
    const res = await this.client.request<ConversationListItem[]>({
      method: 'GET',
      path: `/agents/${agentId}/conversations`,
      query: {
        page,
        limit: query.limit,
        search: query.search,
        channel: query.channel,
        is_test_channel: query.is_test_channel,
        is_ai_chat_paused: query.is_ai_chat_paused,
        needs_attention: query.needs_attention,
      },
    });
    return new Page<ConversationListItem>({
      data: res.data,
      meta: res.meta,
      requestId: res.requestId,
      fetcher: (next) => this.fetchPage(agentId, next, query),
    });
  }
}
