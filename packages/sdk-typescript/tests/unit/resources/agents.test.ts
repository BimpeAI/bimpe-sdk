import { describe, expect, it, vi } from 'vitest';
import { Page } from '../../../src/core/pagination';
import { Agents } from '../../../src/resources/agents/agents';

const okResponse = <T>(data: T, meta: unknown = null) => ({
  data,
  meta,
  requestId: 'r1',
  status: 200,
  headers: new Headers(),
});

const makeAgents = (requestImpl: ReturnType<typeof vi.fn>) =>
  new Agents({ request: requestImpl } as never);

describe('Agents resource', () => {
  it('list() calls GET /agents with query and returns a Page', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse([{ id: 'a_1' }], {
        total_count: 1,
        page_count: 1,
        current_page: 1,
        limit: 50,
        has_next_page: false,
        has_previous_page: false,
      }),
    );
    const page = await makeAgents(requestImpl).list({ page: 1, limit: 50, sort: '-created_at' });
    expect(page).toBeInstanceOf(Page);
    expect(page.data).toEqual([{ id: 'a_1' }]);
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/agents',
      query: { page: 1, limit: 50, search: undefined, sort: '-created_at' },
    });
  });

  it('create() POSTs /agents with body and idempotency option', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ id: 'a_1' }));
    const agent = await makeAgents(requestImpl).create(
      { name: 'Hello' },
      { idempotencyKey: 'op-1' },
    );
    expect(agent.id).toBe('a_1');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents',
      body: { name: 'Hello' },
      idempotencyKey: 'op-1',
    });
  });

  it('retrieve() GETs /agents/{id}', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        id: 'a_1',
        integration: [],
        channel: [],
        conversation_flow: [],
        actions: [],
        knowledge_bases: [],
      }),
    );
    const detail = await makeAgents(requestImpl).retrieve('a_1');
    expect(detail.id).toBe('a_1');
    expect(requestImpl).toHaveBeenCalledWith({ method: 'GET', path: '/agents/a_1' });
  });

  it('update() PATCHes /agents/{id} with body', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ id: 'a_1', name: 'New' }));
    const updated = await makeAgents(requestImpl).update('a_1', { name: 'New' });
    expect(updated.name).toBe('New');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'PATCH',
      path: '/agents/a_1',
      body: { name: 'New' },
    });
  });
});
