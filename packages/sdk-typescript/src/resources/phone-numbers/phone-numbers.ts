import { Page, PagePromise } from '../../core/pagination';
import type { ListQuery, RequestExecutor, RequestOptions } from '../../core/types';
import { PhoneNumberRequests } from './requests';
import type { PhoneNumber, PhoneNumberDetail, UpdatePhoneNumberBody } from './types';

export class PhoneNumbers {
  readonly requests: PhoneNumberRequests;

  constructor(private readonly client: RequestExecutor) {
    this.requests = new PhoneNumberRequests(client);
  }

  list(query: ListQuery = {}): PagePromise<PhoneNumber> {
    return new PagePromise(() => this.fetchPage(query.page ?? 1, query));
  }

  async retrieve(phoneNumberId: string): Promise<PhoneNumberDetail> {
    const res = await this.client.request<PhoneNumberDetail>({
      method: 'GET',
      path: `/phone-numbers/${phoneNumberId}`,
    });
    return res.data;
  }

  async update(
    phoneNumberId: string,
    body: UpdatePhoneNumberBody,
    options: RequestOptions = {},
  ): Promise<PhoneNumberDetail> {
    const res = await this.client.request<PhoneNumberDetail>({
      method: 'PATCH',
      path: `/phone-numbers/${phoneNumberId}`,
      body,
      ...options,
    });
    return res.data;
  }

  private async fetchPage(page: number, query: ListQuery): Promise<Page<PhoneNumber>> {
    const res = await this.client.request<PhoneNumber[]>({
      method: 'GET',
      path: '/phone-numbers',
      query: { page, limit: query.limit, search: query.search, sort: query.sort },
    });
    return new Page<PhoneNumber>({
      data: res.data,
      meta: res.meta,
      requestId: res.requestId,
      fetcher: (next) => this.fetchPage(next, query),
    });
  }
}
