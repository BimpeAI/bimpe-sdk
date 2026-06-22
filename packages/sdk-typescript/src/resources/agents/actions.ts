import type { RequestExecutor, RequestOptions } from '../../core/types';
import type { AgentAction, BulkActionIdsBody, BulkActionUpdate } from './types';

export class AgentActions {
  constructor(private readonly client: RequestExecutor) {}

  async list(agentId: string): Promise<readonly AgentAction[]> {
    const res = await this.client.request<AgentAction[]>({
      method: 'GET',
      path: `/agents/${agentId}/actions`,
    });
    return res.data;
  }

  async enable(
    agentId: string,
    body: BulkActionIdsBody,
    options: RequestOptions = {},
  ): Promise<BulkActionUpdate> {
    const res = await this.client.request<BulkActionUpdate>({
      method: 'POST',
      path: `/agents/${agentId}/actions/enable`,
      body,
      ...options,
    });
    return res.data;
  }

  async disable(
    agentId: string,
    body: BulkActionIdsBody,
    options: RequestOptions = {},
  ): Promise<BulkActionUpdate> {
    const res = await this.client.request<BulkActionUpdate>({
      method: 'POST',
      path: `/agents/${agentId}/actions/disable`,
      body,
      ...options,
    });
    return res.data;
  }
}
