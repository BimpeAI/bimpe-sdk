import type { PaginationMeta } from './types';

export type PageFetcher<T> = (page: number) => Promise<Page<T>>;

export interface PageInit<T> {
  data: readonly T[];
  meta: PaginationMeta | null;
  requestId: string | null;
  fetcher: PageFetcher<T>;
}

export class Page<T> implements AsyncIterable<T> {
  readonly data: readonly T[];
  readonly meta: PaginationMeta | null;
  readonly requestId: string | null;
  private readonly fetcher: PageFetcher<T>;

  constructor(init: PageInit<T>) {
    this.data = init.data;
    this.meta = init.meta;
    this.requestId = init.requestId;
    this.fetcher = init.fetcher;
  }

  get hasNextPage(): boolean {
    return this.meta?.has_next_page === true;
  }

  async getNextPage(): Promise<Page<T> | null> {
    if (!this.hasNextPage || !this.meta) return null;
    return this.fetcher(this.meta.current_page + 1);
  }

  async *[Symbol.asyncIterator](): AsyncIterator<T> {
    let cursor: Page<T> | null = this;
    while (cursor) {
      for (const item of cursor.data) yield item;
      cursor = await cursor.getNextPage();
    }
  }

  async *pages(): AsyncGenerator<Page<T>> {
    let cursor: Page<T> | null = this;
    while (cursor) {
      yield cursor;
      cursor = await cursor.getNextPage();
    }
  }
}
