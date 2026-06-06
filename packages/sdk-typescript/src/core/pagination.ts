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

/**
 * The return value of a `list` call. Awaiting it yields the first `Page`; iterating
 * it with `for await` walks every item across all pages, fetching lazily.
 */
export class PagePromise<T> implements PromiseLike<Page<T>>, AsyncIterable<T> {
  private readonly load: () => Promise<Page<T>>;

  constructor(load: () => Promise<Page<T>>) {
    this.load = load;
  }

  // biome-ignore lint/suspicious/noThenProperty: this is an intentional thenable so list() can be awaited
  then<TResult1 = Page<T>, TResult2 = never>(
    onfulfilled?: ((value: Page<T>) => TResult1 | PromiseLike<TResult1>) | null,
    onrejected?: ((reason: unknown) => TResult2 | PromiseLike<TResult2>) | null,
  ): Promise<TResult1 | TResult2> {
    return this.load().then(onfulfilled, onrejected);
  }

  catch<TResult = never>(
    onrejected?: ((reason: unknown) => TResult | PromiseLike<TResult>) | null,
  ): Promise<Page<T> | TResult> {
    return this.load().then(undefined, onrejected);
  }

  finally(onfinally?: (() => void) | null): Promise<Page<T>> {
    return this.load().finally(onfinally);
  }

  async *[Symbol.asyncIterator](): AsyncIterator<T> {
    const first = await this.load();
    yield* first;
  }

  pages(): AsyncIterable<Page<T>> {
    const load = this.load;
    return {
      async *[Symbol.asyncIterator]() {
        const first = await load();
        yield* first.pages();
      },
    };
  }
}
