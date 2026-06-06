import { Page, PagePromise } from '../../core/pagination';
import type { RequestExecutor, RequestOptions } from '../../core/types';
import type {
  CreateWorkflowBody,
  ListWorkflowsQuery,
  UpdateWorkflowBody,
  Workflow,
  WorkflowSummary,
} from './types';

type Client = RequestExecutor;

export class Workflows {
  constructor(private readonly client: Client) {}

  list(query: ListWorkflowsQuery = {}): PagePromise<WorkflowSummary> {
    return new PagePromise(() => this.fetchPage(query.page ?? 1, query));
  }

  async create(body: CreateWorkflowBody, options: RequestOptions = {}): Promise<Workflow> {
    const res = await this.client.request<Workflow>({
      method: 'POST',
      path: '/workflows',
      body,
      ...options,
    });
    return res.data;
  }

  async retrieve(workflowId: string): Promise<Workflow> {
    const res = await this.client.request<Workflow>({
      method: 'GET',
      path: `/workflows/${workflowId}`,
    });
    return res.data;
  }

  async update(workflowId: string, body: UpdateWorkflowBody): Promise<Workflow> {
    const res = await this.client.request<Workflow>({
      method: 'PATCH',
      path: `/workflows/${workflowId}`,
      body,
    });
    return res.data;
  }

  async delete(workflowId: string): Promise<void> {
    await this.client.request<null>({
      method: 'DELETE',
      path: `/workflows/${workflowId}`,
    });
  }

  private async fetchPage(page: number, query: ListWorkflowsQuery): Promise<Page<WorkflowSummary>> {
    const res = await this.client.request<WorkflowSummary[]>({
      method: 'GET',
      path: '/workflows',
      query: {
        page,
        limit: query.limit,
        search: query.search,
        sort: query.sort,
        scope: query.scope,
      },
    });
    return new Page<WorkflowSummary>({
      data: res.data,
      meta: res.meta,
      requestId: res.requestId,
      fetcher: (next) => this.fetchPage(next, query),
    });
  }
}
