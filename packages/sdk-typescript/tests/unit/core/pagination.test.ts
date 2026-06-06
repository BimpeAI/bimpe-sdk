import { describe, expect, it } from 'vitest';
import { Page, PagePromise } from '../../../src/core/pagination';
import type { PaginationMeta } from '../../../src/core/types';

const meta = (current: number, hasNext: boolean): PaginationMeta => ({
  total_count: 5,
  page_count: 3,
  current_page: current,
  limit: 2,
  has_next_page: hasNext,
  has_previous_page: current > 1,
});

const pageData: Record<number, number[]> = { 1: [1, 2], 2: [3, 4], 3: [5] };

function fetchPage(page: number): Promise<Page<number>> {
  const data = pageData[page];
  if (!data) throw new Error(`unexpected page ${page}`);
  return Promise.resolve(
    new Page<number>({
      data,
      meta: meta(page, page < 3),
      requestId: `r${page}`,
      fetcher: fetchPage,
    }),
  );
}

describe('Page', () => {
  it('exposes data, meta, requestId, hasNextPage', async () => {
    const p = await fetchPage(1);
    expect(p.data).toEqual([1, 2]);
    expect(p.meta?.current_page).toBe(1);
    expect(p.requestId).toBe('r1');
    expect(p.hasNextPage).toBe(true);
  });

  it('returns null from getNextPage on the last page', async () => {
    const last = await fetchPage(3);
    expect(last.hasNextPage).toBe(false);
    expect(await last.getNextPage()).toBeNull();
  });

  it('iterates items across all pages with for-await', async () => {
    const first = await fetchPage(1);
    const items: number[] = [];
    for await (const item of first) items.push(item);
    expect(items).toEqual([1, 2, 3, 4, 5]);
  });

  it('iterates pages with .pages()', async () => {
    const first = await fetchPage(1);
    const pages: number[] = [];
    for await (const p of first.pages()) pages.push(p.meta?.current_page ?? -1);
    expect(pages).toEqual([1, 2, 3]);
  });

  it('honors early break in item iteration', async () => {
    const first = await fetchPage(1);
    const items: number[] = [];
    for await (const item of first) {
      items.push(item);
      if (item === 3) break;
    }
    expect(items).toEqual([1, 2, 3]);
  });
});

describe('PagePromise', () => {
  it('awaits to the first page', async () => {
    const promise = new PagePromise<number>(() => fetchPage(1));
    const page = await promise;
    expect(page).toBeInstanceOf(Page);
    expect(page.data).toEqual([1, 2]);
  });

  it('iterates items across all pages with for-await directly on the promise', async () => {
    const promise = new PagePromise<number>(() => fetchPage(1));
    const items: number[] = [];
    for await (const item of promise) items.push(item);
    expect(items).toEqual([1, 2, 3, 4, 5]);
  });

  it('walks pages with .pages()', async () => {
    const promise = new PagePromise<number>(() => fetchPage(1));
    const seen: number[] = [];
    for await (const p of promise.pages()) seen.push(p.meta?.current_page ?? -1);
    expect(seen).toEqual([1, 2, 3]);
  });
});
