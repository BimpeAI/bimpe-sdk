import { Page, PagePromise } from '../../core/pagination';
import type { ListQuery, RequestExecutor, RequestOptions } from '../../core/types';
import type { CreatePhoneNumberRequestBody, PhoneNumberRequest } from './types';

export class PhoneNumberRequests {
  constructor(private readonly client: RequestExecutor) {}

  list(query: ListQuery = {}): PagePromise<PhoneNumberRequest> {
    return new PagePromise(() => this.fetchPage(query.page ?? 1, query));
  }

  async create(body: CreatePhoneNumberRequestBody, options: RequestOptions = {}): Promise<void> {
    await this.client.request<unknown>({
      method: 'POST',
      path: '/phone-numbers/request',
      body,
      ...options,
    });
  }

  private async fetchPage(page: number, query: ListQuery): Promise<Page<PhoneNumberRequest>> {
    const res = await this.client.request<PhoneNumberRequest[]>({
      method: 'GET',
      path: '/phone-numbers/request',
      query: { page, limit: query.limit, search: query.search, sort: query.sort },
    });
    return new Page<PhoneNumberRequest>({
      data: res.data,
      meta: res.meta,
      requestId: res.requestId,
      fetcher: (next) => this.fetchPage(next, query),
    });
  }
}
