import { http, HttpResponse } from 'msw';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import { BimpeAI } from '../../src';
import { API_BASE, createMswServer } from '../helpers/msw-server';

let seenKeys: string[] = [];
let fails = 2;

const server = createMswServer([
  http.post(`${API_BASE}/agents`, ({ request }) => {
    const key = request.headers.get('idempotency-key');
    if (key) seenKeys.push(key);
    if (fails > 0) {
      fails -= 1;
      return HttpResponse.json({ message: 'oops' }, { status: 500 });
    }
    return HttpResponse.json(
      { message: 'created', data: { id: 'a_1', name: 'A' } },
      { status: 201 },
    );
  }),
]);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  seenKeys = [];
  fails = 2;
});
afterAll(() => server.close());

describe('idempotency integration', () => {
  it('reuses the caller-supplied key across retries', async () => {
    const client = new BimpeAI({
      apiKey: 'sk_test',
      baseUrl: 'https://api.bimpeai.test',
      maxRetries: 3,
    });
    await client.agents.create(
      { workflow_id: 'wf_1', name: 'A', description: 'Test agent' },
      { idempotencyKey: 'op-123' },
    );
    expect(seenKeys).toEqual(['op-123', 'op-123', 'op-123']);
  });

  it('auto-generates one key and reuses it across retries when none supplied', async () => {
    const client = new BimpeAI({
      apiKey: 'sk_test',
      baseUrl: 'https://api.bimpeai.test',
      maxRetries: 3,
    });
    await client.agents.create({
      workflow_id: 'wf_1',
      name: 'A',
      description: 'Test agent',
    });
    expect(seenKeys).toHaveLength(3);
    expect(new Set(seenKeys).size).toBe(1);
  });
});
