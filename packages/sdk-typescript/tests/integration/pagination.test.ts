import { http, HttpResponse } from 'msw';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import { BimpeAI } from '../../src';
import { API_BASE, createMswServer } from '../helpers/msw-server';

const pages: Record<string, { data: { id: string }[]; current: number; hasNext: boolean }> = {
  '1': { data: [{ id: 'a_1' }, { id: 'a_2' }], current: 1, hasNext: true },
  '2': { data: [{ id: 'a_3' }, { id: 'a_4' }], current: 2, hasNext: true },
  '3': { data: [{ id: 'a_5' }], current: 3, hasNext: false },
};

const server = createMswServer([
  http.get(`${API_BASE}/agents`, ({ request }) => {
    const page = new URL(request.url).searchParams.get('page') ?? '1';
    const found = pages[page];
    if (!found) return HttpResponse.json({ message: 'no page' }, { status: 404 });
    return HttpResponse.json({
      message: 'ok',
      data: found.data,
      meta: {
        total_count: 5,
        page_count: 3,
        current_page: found.current,
        limit: 2,
        has_next_page: found.hasNext,
        has_previous_page: found.current > 1,
      },
    });
  }),
]);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('pagination integration', () => {
  it('iterates every item across pages with for-await', async () => {
    const client = new BimpeAI({ apiKey: 'sk_test', baseUrl: 'https://api.bimpeai.test' });
    const ids: string[] = [];
    for await (const agent of client.agents.list({ limit: 2 })) ids.push(agent.id);
    expect(ids).toEqual(['a_1', 'a_2', 'a_3', 'a_4', 'a_5']);
  });

  it('walks pages with .pages()', async () => {
    const client = new BimpeAI({ apiKey: 'sk_test', baseUrl: 'https://api.bimpeai.test' });
    const first = await client.agents.list({ limit: 2 });
    const seen: number[] = [];
    for await (const page of first.pages()) seen.push(page.meta?.current_page ?? -1);
    expect(seen).toEqual([1, 2, 3]);
  });

  it('stops fetching on early break', async () => {
    const client = new BimpeAI({ apiKey: 'sk_test', baseUrl: 'https://api.bimpeai.test' });
    const ids: string[] = [];
    for await (const agent of client.agents.list({ limit: 2 })) {
      ids.push(agent.id);
      if (agent.id === 'a_3') break;
    }
    expect(ids).toEqual(['a_1', 'a_2', 'a_3']);
  });
});
