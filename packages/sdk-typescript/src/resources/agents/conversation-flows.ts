import type { RequestExecutor } from '../../core/types';
import type { AgentConversationFlow } from './types';

export class AgentConversationFlows {
  constructor(private readonly client: RequestExecutor) {}

  async list(agentId: string): Promise<readonly AgentConversationFlow[]> {
    const res = await this.client.request<AgentConversationFlow[]>({
      method: 'GET',
      path: `/agents/${agentId}/conversation_flows`,
    });
    return res.data;
  }
}
