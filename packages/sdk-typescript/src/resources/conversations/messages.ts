import type { HttpClient } from '../../core/http-client';
import { Page } from '../../core/pagination';
import type { RequestOptions } from '../../core/types';
import type { ListMessagesQuery, Message, SendMessageBody } from './types';

type Client = Pick<HttpClient, 'request'>;

export class Messages {
  constructor(private readonly client: Client) {}

  list(
    agentId: string,
    conversationId: string,
    query: ListMessagesQuery = {},
  ): Promise<Page<Message>> {
    return this.fetchPage(agentId, conversationId, query.page ?? 1, query);
  }

  async send(
    agentId: string,
    conversationId: string,
    body: SendMessageBody,
    options: RequestOptions = {},
  ): Promise<Message> {
    const res = await this.client.request<Message>({
      method: 'POST',
      path: `/agents/${agentId}/conversations/${conversationId}/messages`,
      body,
      ...options,
    });
    return res.data;
  }

  private async fetchPage(
    agentId: string,
    conversationId: string,
    page: number,
    query: ListMessagesQuery,
  ): Promise<Page<Message>> {
    const res = await this.client.request<Message[]>({
      method: 'GET',
      path: `/agents/${agentId}/conversations/${conversationId}/messages`,
      query: { page, limit: query.limit },
    });
    return new Page<Message>({
      data: res.data,
      meta: res.meta,
      requestId: res.requestId,
      fetcher: (next) => this.fetchPage(agentId, conversationId, next, query),
    });
  }
}
