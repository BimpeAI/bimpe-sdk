import { http, HttpResponse, delay } from 'msw';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import { BimpeAI, ConnectionError, ConnectionTimeoutError } from '../../src';
import { API_BASE, createMswServer } from '../helpers/msw-server';

const server = createMswServer([
  http.get(`${API_BASE}/agents`, async () => {
    await delay(200);
    return HttpResponse.json({
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
    });
  }),
]);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('timeout and abort integration', () => {
  it('throws ConnectionTimeoutError when the client timeout elapses', async () => {
    const client = new BimpeAI({
      apiKey: 'sk_test',
      baseUrl: 'https://api.bimpeai.test',
      timeout: 20,
      maxRetries: 0,
    });
    await expect(client.agents.list()).rejects.toBeInstanceOf(ConnectionTimeoutError);
  });

  it('throws ConnectionError when the caller aborts', async () => {
    const client = new BimpeAI({
      apiKey: 'sk_test',
      baseUrl: 'https://api.bimpeai.test',
      maxRetries: 0,
    });
    const ac = new AbortController();
    queueMicrotask(() => ac.abort());
    await expect(
      client.request({ method: 'GET', path: '/agents', signal: ac.signal }),
    ).rejects.toBeInstanceOf(ConnectionError);
  });
});
