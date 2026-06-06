import type { RequestExecutor } from '../../core/types';
import type { AgentActionSummary } from './types';

export class AgentActions {
  constructor(private readonly client: RequestExecutor) {}

  async list(agentId: string): Promise<readonly AgentActionSummary[]> {
    const res = await this.client.request<AgentActionSummary[]>({
      method: 'GET',
      path: `/agents/${agentId}/actions`,
    });
    return res.data;
  }
}
