import { Page, PagePromise } from '../../core/pagination';
import type { RequestExecutor } from '../../core/types';
import { Messages } from './messages';
import type { Conversation, ListConversationsQuery } from './types';

type Client = RequestExecutor;

export class Conversations {
  readonly messages: Messages;

  constructor(private readonly client: Client) {
    this.messages = new Messages(client);
  }

  list(agentId: string, query: ListConversationsQuery = {}): PagePromise<Conversation> {
    return new PagePromise(() => this.fetchPage(agentId, query.page ?? 1, query));
  }

  async retrieve(agentId: string, conversationId: string): Promise<Conversation> {
    const res = await this.client.request<Conversation>({
      method: 'GET',
      path: `/agents/${agentId}/conversations/${conversationId}`,
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
      query: { page, limit: query.limit, search: query.search, channel: query.channel },
    });
    return new Page<Conversation>({
      data: res.data,
      meta: res.meta,
      requestId: res.requestId,
      fetcher: (next) => this.fetchPage(agentId, next, query),
    });
  }
}
