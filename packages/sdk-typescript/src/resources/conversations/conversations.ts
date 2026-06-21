import { Page, PagePromise } from '../../core/pagination';
import type { RequestOptions, Transport } from '../../core/types';
import { Messages } from './messages';
import type {
  Conversation,
  ConversationAiStatus,
  ConversationDetail,
  CreateConversationMessageBody,
  ListConversationsQuery,
  Message,
  SetAiStatusBody,
} from './types';

type Client = Transport;

export class Conversations {
  readonly messages: Messages;

  constructor(private readonly client: Client) {
    this.messages = new Messages(client);
  }

  list(agentId: string, query: ListConversationsQuery = {}): PagePromise<Conversation> {
    return new PagePromise(() => this.fetchPage(agentId, query.page ?? 1, query));
  }

  async retrieve(agentId: string, conversationId: string): Promise<ConversationDetail> {
    const res = await this.client.request<ConversationDetail>({
      method: 'GET',
      path: `/agents/${agentId}/conversations/${conversationId}`,
    });
    return res.data;
  }

  async send(
    agentId: string,
    body: CreateConversationMessageBody,
    options: RequestOptions = {},
  ): Promise<Message> {
    const res = await this.client.request<Message>({
      method: 'POST',
      path: `/agents/${agentId}/conversations/messages`,
      body,
      ...options,
    });
    return res.data;
  }

  async setAiStatus(
    agentId: string,
    conversationId: string,
    body: SetAiStatusBody,
    options: RequestOptions = {},
  ): Promise<ConversationAiStatus> {
    const res = await this.client.request<ConversationAiStatus>({
      method: 'PATCH',
      path: `/agents/${agentId}/conversations/${conversationId}/ai-status`,
      body,
      ...options,
    });
    return res.data;
  }

  private async fetchPage(
    agentId: string,
    page: number,
    query: ListConversationsQuery,
  ): Promise<Page<Conversation>> {
    const res = await this.client.request<Conversation[]>({
      method: 'GET',
      path: `/agents/${agentId}/conversations`,
      query: {
        page,
        limit: query.limit,
        search: query.search,
        sort: query.sort,
        channel: query.channel,
        is_test_channel: query.is_test_channel,
        is_ai_chat_paused: query.is_ai_chat_paused,
        needs_attention: query.needs_attention,
      },
    });
    return new Page<Conversation>({
      data: res.data,
      meta: res.meta,
      requestId: res.requestId,
      fetcher: (next) => this.fetchPage(agentId, next, query),
    });
  }
}
