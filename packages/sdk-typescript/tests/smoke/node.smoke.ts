import assert from 'node:assert/strict';
import { BimpeAI, VERSION } from '../../dist/index.js';

const fetchMock: typeof fetch = async () =>
  new Response(
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
    { status: 200, headers: { 'content-type': 'application/json', 'x-request-id': 'r_smoke' } },
  );

const client = new BimpeAI({ apiKey: 'sk_smoke', fetch: fetchMock });
const page = await client.agents.list();
assert.equal(page.data.length, 0);
assert.equal(page.requestId, 'r_smoke');
assert.match(VERSION, /^\d+\.\d+\.\d+/);
console.log('node smoke ok');
