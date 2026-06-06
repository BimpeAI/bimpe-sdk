import { http, HttpResponse } from 'msw';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import { BimpeAI, InternalServerError, NotFoundError } from '../../src';
import { API_BASE, createMswServer } from '../helpers/msw-server';

let count = 0;

const server = createMswServer([
  http.get(`${API_BASE}/agents`, () => {
    count += 1;
    if (count < 3) return HttpResponse.json({ message: 'oops' }, { status: 500 });
    return HttpResponse.json({
      message: 'ok',
      data: [{ id: 'a_1' }],
      meta: {
        total_count: 1,
        page_count: 1,
        current_page: 1,
        limit: 20,
        has_next_page: false,
        has_previous_page: false,
      },
    });
  }),
  http.get(`${API_BASE}/agents/missing`, () =>
    HttpResponse.json({ message: 'nope' }, { status: 404 }),
  ),
]);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  count = 0;
});
afterAll(() => server.close());

describe('retries integration', () => {
  it('retries 500s and succeeds within maxRetries', async () => {
    const client = new BimpeAI({
      apiKey: 'sk_test',
      baseUrl: 'https://api.bimpeai.test',
      maxRetries: 3,
    });
    const page = await client.agents.list();
    expect(page.data).toEqual([{ id: 'a_1' }]);
    expect(count).toBe(3);
  });

  it('does not retry 404s', async () => {
    const client = new BimpeAI({
      apiKey: 'sk_test',
      baseUrl: 'https://api.bimpeai.test',
      maxRetries: 3,
    });
    await expect(client.agents.retrieve('missing')).rejects.toBeInstanceOf(NotFoundError);
  });

  it('gives up after exhausting maxRetries', async () => {
    server.use(
      http.get(`${API_BASE}/agents`, () => HttpResponse.json({ message: 'down' }, { status: 503 })),
    );
    const client = new BimpeAI({
      apiKey: 'sk_test',
      baseUrl: 'https://api.bimpeai.test',
      maxRetries: 1,
    });
    await expect(client.agents.list()).rejects.toBeInstanceOf(InternalServerError);
  });
});
