import type { HttpClient } from '../../core/http-client';
import type { AgentConversationFlow } from './types';

export class AgentConversationFlows {
  constructor(private readonly client: Pick<HttpClient, 'request'>) {}

  async list(agentId: string): Promise<readonly AgentConversationFlow[]> {
    const res = await this.client.request<AgentConversationFlow[]>({
      method: 'GET',
      path: `/agents/${agentId}/conversation_flows`,
    });
    return res.data;
  }
}
