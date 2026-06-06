import type { HttpClient } from '../../core/http-client';
import { Page } from '../../core/pagination';
import type { ListQuery, RequestOptions } from '../../core/types';
import type { Agent, AgentDetail, CreateAgentBody, UpdateAgentBody } from './types';

type Client = Pick<HttpClient, 'request'>;

export class Agents {
  constructor(private readonly client: Client) {}

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
