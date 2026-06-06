import type { RequestExecutor } from '../../core/types';
import type { AgentChannel } from './types';

export class AgentChannels {
  constructor(private readonly client: RequestExecutor) {}

  async list(agentId: string): Promise<readonly AgentChannel[]> {
    const res = await this.client.request<AgentChannel[]>({
      method: 'GET',
      path: `/agents/${agentId}/channels`,
    });
    return res.data;
  }
}
