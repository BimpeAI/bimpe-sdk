import { http, HttpResponse } from 'msw';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import { BimpeAI } from '../../src';
import { API_BASE, createMswServer } from '../helpers/msw-server';

let lastSeenRequestId = '';

const server = createMswServer([
  http.get(`${API_BASE}/agents`, ({ request }) => {
    lastSeenRequestId = request.headers.get('x-request-id') ?? '';
    return new HttpResponse(
      JSON.stringify({
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
      }),
      {
        status: 200,
        headers: { 'content-type': 'application/json', 'x-request-id': lastSeenRequestId },
      },
    );
  }),
]);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  lastSeenRequestId = '';
});
afterAll(() => server.close());

describe('x-request-id integration', () => {
  it('sends a generated request id and echoes the server value back', async () => {
    const client = new BimpeAI({ apiKey: 'sk_test', baseUrl: 'https://api.bimpeai.test' });
    const page = await client.agents.list();
    expect(lastSeenRequestId).toMatch(/^[0-9a-f-]{36}$/);
    expect(page.requestId).toBe(lastSeenRequestId);
  });
});
