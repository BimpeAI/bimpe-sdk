import type { RequestExecutor, RequestOptions } from '../../core/types';
import type { CreateKnowledgeBaseBody, KnowledgeBaseItem, UpdateKnowledgeBaseBody } from './types';

export class AgentKnowledgeBases {
  constructor(private readonly client: RequestExecutor) {}

  async list(agentId: string): Promise<readonly KnowledgeBaseItem[]> {
    const res = await this.client.request<KnowledgeBaseItem[]>({
      method: 'GET',
      path: `/agents/${agentId}/knowledge_bases`,
    });
    return res.data;
  }

  async create(
    agentId: string,
    body: CreateKnowledgeBaseBody,
    options: RequestOptions = {},
  ): Promise<KnowledgeBaseItem> {
    const res = await this.client.request<KnowledgeBaseItem>({
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
  ): Promise<KnowledgeBaseItem> {
    const res = await this.client.request<KnowledgeBaseItem>({
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
