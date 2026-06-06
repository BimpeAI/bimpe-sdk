import type { HttpClient } from '../../core/http-client';
import { Page } from '../../core/pagination';
import type { ListQuery, RequestOptions } from '../../core/types';
import { AgentActions } from './actions';
import { AgentChannels } from './channels';
import { AgentConversationFlows } from './conversation-flows';
import { AgentIntegrations } from './integrations';
import { AgentKnowledgeBases } from './knowledge-bases';
import type { Agent, AgentDetail, CreateAgentBody, UpdateAgentBody } from './types';

type Client = Pick<HttpClient, 'request'>;

export class Agents {
  readonly integrations: AgentIntegrations;
  readonly channels: AgentChannels;
  readonly conversationFlows: AgentConversationFlows;
  readonly actions: AgentActions;
  readonly knowledgeBases: AgentKnowledgeBases;

  constructor(private readonly client: Client) {
    this.integrations = new AgentIntegrations(client);
    this.channels = new AgentChannels(client);
    this.conversationFlows = new AgentConversationFlows(client);
    this.actions = new AgentActions(client);
    this.knowledgeBases = new AgentKnowledgeBases(client);
  }

  list(query: ListQuery = {}): Promise<Page<Agent>> {
    return this.fetchPage(query.page ?? 1, query);
  }

  async create(body: CreateAgentBody, options: RequestOptions = {}): Promise<Agent> {
    const res = await this.client.request<Agent>({
      method: 'POST',
      path: '/agents',
      body,
      ...options,
    });
    return res.data;
  }

  async retrieve(agentId: string): Promise<AgentDetail> {
    const res = await this.client.request<AgentDetail>({
      method: 'GET',
      path: `/agents/${agentId}`,
    });
    return res.data;
  }

  async update(agentId: string, body: UpdateAgentBody): Promise<Agent> {
    const res = await this.client.request<Agent>({
      method: 'PATCH',
      path: `/agents/${agentId}`,
      body,
    });
    return res.data;
  }

  private async fetchPage(page: number, query: ListQuery): Promise<Page<Agent>> {
    const res = await this.client.request<Agent[]>({
      method: 'GET',
      path: '/agents',
      query: { page, limit: query.limit, search: query.search, sort: query.sort },
    });
    return new Page<Agent>({
      data: res.data,
      meta: res.meta,
      requestId: res.requestId,
      fetcher: (next) => this.fetchPage(next, query),
    });
  }
}
