import { Page, PagePromise } from '../../core/pagination';
import type { RequestExecutor, RequestOptions } from '../../core/types';
import type { Call, CallDetail, ListCallsQuery, MakeCallBody, MakeCallResult } from './types';

export class Calls {
  constructor(private readonly client: RequestExecutor) {}

  list(agentId: string, query: ListCallsQuery = {}): PagePromise<Call> {
    return new PagePromise(() => this.fetchPage(agentId, query.page ?? 1, query));
  }

  async make(
    agentId: string,
    body: MakeCallBody,
    options: RequestOptions = {},
  ): Promise<MakeCallResult> {
    const res = await this.client.request<MakeCallResult>({
      method: 'POST',
      path: `/agents/${agentId}/calls`,
      body,
      ...options,
    });
    return res.data;
  }

  async retrieve(agentId: string, callId: string): Promise<CallDetail> {
    const res = await this.client.request<CallDetail>({
      method: 'GET',
      path: `/agents/${agentId}/calls/${callId}`,
    });
    return res.data;
  }

  private async fetchPage(
    agentId: string,
    page: number,
    query: ListCallsQuery,
  ): Promise<Page<Call>> {
    const res = await this.client.request<Call[]>({
      method: 'GET',
      path: `/agents/${agentId}/calls`,
      query: {
        page,
        limit: query.limit,
        search: query.search,
        sort: query.sort,
        is_test_call: query.is_test_call,
        status: query.status,
      },
    });
    return new Page<Call>({
      data: res.data,
      meta: res.meta,
      requestId: res.requestId,
      fetcher: (next) => this.fetchPage(agentId, next, query),
    });
  }
}
