import { Page, PagePromise } from '../../core/pagination';
import type { ListQuery, RequestExecutor, RequestOptions } from '../../core/types';
import { AgentActions } from './actions';
import { AgentChannels } from './channels';
import { AgentIntegrations } from './integrations';
import { AgentKnowledgeBases } from './knowledge-bases';
import type {
  Agent,
  AgentCreateResponse,
  AgentDetail,
  AgentLiveStatus,
  AgentTestCode,
  CreateAgentBody,
  UpdateAgentBody,
  UpdateLiveStatusBody,
} from './types';

type Client = RequestExecutor;

export class Agents {
  readonly integrations: AgentIntegrations;
  readonly channels: AgentChannels;
  readonly actions: AgentActions;
  readonly knowledgeBases: AgentKnowledgeBases;

  constructor(private readonly client: Client) {
    this.integrations = new AgentIntegrations(client);
    this.channels = new AgentChannels(client);
    this.actions = new AgentActions(client);
    this.knowledgeBases = new AgentKnowledgeBases(client);
  }

  list(query: ListQuery = {}): PagePromise<Agent> {
    return new PagePromise(() => this.fetchPage(query.page ?? 1, query));
  }

  async create(body: CreateAgentBody, options: RequestOptions = {}): Promise<AgentCreateResponse> {
    const res = await this.client.request<AgentCreateResponse>({
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

  async delete(agentId: string): Promise<void> {
    await this.client.request<null>({
      method: 'DELETE',
      path: `/agents/${agentId}`,
    });
  }

  async updateLiveStatus(
    agentId: string,
    body: UpdateLiveStatusBody,
    options: RequestOptions = {},
  ): Promise<AgentLiveStatus> {
    const res = await this.client.request<AgentLiveStatus>({
      method: 'PATCH',
      path: `/agents/${agentId}/live-status`,
      body,
      ...options,
    });
    return res.data;
  }

  async getTestCode(agentId: string): Promise<AgentTestCode> {
    const res = await this.client.request<AgentTestCode>({
      method: 'GET',
      path: `/agents/${agentId}/deployment/agent-test-code`,
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
