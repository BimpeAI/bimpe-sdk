import { http, HttpResponse } from 'msw';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import { BimpeAI, RateLimitError } from '../../src';
import { API_BASE, createMswServer } from '../helpers/msw-server';

let firstHit = true;

const server = createMswServer([
  http.get(`${API_BASE}/agents`, () => {
    if (firstHit) {
      firstHit = false;
      return new HttpResponse(JSON.stringify({ message: 'slow' }), {
        status: 429,
        headers: {
          'content-type': 'application/json',
          'retry-after': '0',
          'x-ratelimit-limit': '60',
          'x-ratelimit-remaining': '0',
        },
      });
    }
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
afterEach(() => {
  server.resetHandlers();
  firstHit = true;
});
afterAll(() => server.close());

describe('rate-limit integration', () => {
  it('retries after a 429 and then succeeds', async () => {
    const client = new BimpeAI({
      apiKey: 'sk_test',
      baseUrl: 'https://api.bimpeai.test',
      maxRetries: 2,
    });
    const page = await client.agents.list();
    expect(page.data).toEqual([]);
  });

  it('exposes RateLimitError metadata when retries are exhausted', async () => {
    server.use(
      http.get(
        `${API_BASE}/agents`,
        () =>
          new HttpResponse(JSON.stringify({ message: 'no' }), {
            status: 429,
            headers: {
              'content-type': 'application/json',
              'retry-after': '5',
              'x-ratelimit-limit': '30',
              'x-ratelimit-remaining': '0',
            },
          }),
      ),
    );
    const client = new BimpeAI({
      apiKey: 'sk_test',
      baseUrl: 'https://api.bimpeai.test',
      maxRetries: 0,
    });
    const error = await client.agents.list().catch((e: unknown) => e);
    expect(error).toBeInstanceOf(RateLimitError);
    const rate = error as RateLimitError;
    expect(rate.retryAfter).toBe(5);
    expect(rate.limit).toBe(30);
    expect(rate.remaining).toBe(0);
  });
});
