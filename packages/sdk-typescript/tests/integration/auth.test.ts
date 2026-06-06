import { http, HttpResponse } from 'msw';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import { AuthenticationError, BimpeAI } from '../../src';
import { API_BASE, createMswServer } from '../helpers/msw-server';

const emptyPage = {
  message: 'ok',
  data: [],
  meta: {
    total_count: 0,
    page_count: 0,
    current_page: 1,
    limit: 20,
    has_next_page: false,
    has_previous_page: false,
  },
};

const server = createMswServer([
  http.get(`${API_BASE}/agents`, ({ request }) => {
    if (request.headers.get('authorization') !== 'Bearer sk_test') {
      return HttpResponse.json({ message: 'bad key', code: 'api_key_invalid' }, { status: 401 });
    }
    return HttpResponse.json(emptyPage);
  }),
]);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('auth integration', () => {
  it('sends the configured bearer key', async () => {
    const client = new BimpeAI({ apiKey: 'sk_test', baseUrl: 'https://api.bimpeai.test' });
    const page = await client.agents.list();
    expect(page.data).toEqual([]);
  });

  it('throws AuthenticationError when the key is rejected', async () => {
    const client = new BimpeAI({
      apiKey: 'sk_wrong',
      baseUrl: 'https://api.bimpeai.test',
      maxRetries: 0,
    });
    await expect(client.agents.list()).rejects.toBeInstanceOf(AuthenticationError);
  });
});
