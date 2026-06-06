import type { RequestExecutor } from '../../core/types';
import type { AgentIntegration } from './types';

export class AgentIntegrations {
  constructor(private readonly client: RequestExecutor) {}

  async list(agentId: string): Promise<readonly AgentIntegration[]> {
    const res = await this.client.request<AgentIntegration[]>({
      method: 'GET',
      path: `/agents/${agentId}/integrations`,
    });
    return res.data;
  }
}
