import type { RequestExecutor } from '../../core/types';
import type { AgentActionSummary, BulkActionIdsBody } from './types';

export class AgentActions {
  constructor(private readonly client: RequestExecutor) {}

  async list(agentId: string): Promise<readonly AgentActionSummary[]> {
    const res = await this.client.request<AgentActionSummary[]>({
      method: 'GET',
      path: `/agents/${agentId}/actions`,
    });
    return res.data;
  }

  async enable(agentId: string, body: BulkActionIdsBody): Promise<unknown> {
    const res = await this.client.request<unknown>({
      method: 'POST',
      path: `/agents/${agentId}/actions/enable`,
      body,
    });
    return res.data;
  }

  async disable(agentId: string, body: BulkActionIdsBody): Promise<unknown> {
    const res = await this.client.request<unknown>({
      method: 'POST',
      path: `/agents/${agentId}/actions/disable`,
      body,
    });
    return res.data;
  }
}
