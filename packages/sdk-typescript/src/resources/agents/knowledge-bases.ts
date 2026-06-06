import type { RequestExecutor, RequestOptions } from '../../core/types';
import type {
  CreateKnowledgeBaseBody,
  KnowledgeBaseSummary,
  UpdateKnowledgeBaseBody,
} from './types';

export class AgentKnowledgeBases {
  constructor(private readonly client: RequestExecutor) {}

  async list(agentId: string): Promise<readonly KnowledgeBaseSummary[]> {
    const res = await this.client.request<KnowledgeBaseSummary[]>({
      method: 'GET',
      path: `/agents/${agentId}/knowledge_bases`,
    });
    return res.data;
  }

  async create(
    agentId: string,
    body: CreateKnowledgeBaseBody,
    options: RequestOptions = {},
  ): Promise<KnowledgeBaseSummary> {
    const res = await this.client.request<KnowledgeBaseSummary>({
      method: 'POST',
      path: `/agents/${agentId}/knowledge_bases`,
      body,
      ...options,
    });
    return res.data;
  }

  async update(
    agentId: string,
    kbId: string,
    body: UpdateKnowledgeBaseBody,
  ): Promise<KnowledgeBaseSummary> {
    const res = await this.client.request<KnowledgeBaseSummary>({
      method: 'PATCH',
      path: `/agents/${agentId}/knowledge_bases/${kbId}`,
      body,
    });
    return res.data;
  }

  async delete(agentId: string, kbId: string): Promise<void> {
    await this.client.request<null>({
      method: 'DELETE',
      path: `/agents/${agentId}/knowledge_bases/${kbId}`,
    });
  }
}
