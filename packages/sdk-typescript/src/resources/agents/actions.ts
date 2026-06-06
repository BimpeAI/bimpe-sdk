import type { HttpClient } from '../../core/http-client';
import type { AgentActionSummary } from './types';

export class AgentActions {
  constructor(private readonly client: Pick<HttpClient, 'request'>) {}

  async list(agentId: string): Promise<readonly AgentActionSummary[]> {
    const res = await this.client.request<AgentActionSummary[]>({
      method: 'GET',
      path: `/agents/${agentId}/actions`,
    });
    return res.data;
  }
}
