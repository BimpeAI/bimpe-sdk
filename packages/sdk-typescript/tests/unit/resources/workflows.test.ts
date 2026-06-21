import { describe, expect, it, vi } from 'vitest';
import { Page } from '../../../src/core/pagination';
import { Workflows } from '../../../src/resources/workflows/workflows';

const okResponse = <T>(data: T, meta: unknown = null) => ({
  data,
  meta,
  requestId: 'r1',
  status: 200,
  headers: new Headers(),
});

const make = (requestImpl: ReturnType<typeof vi.fn>) =>
  new Workflows({ request: requestImpl } as never);

describe('Workflows resource', () => {
  it('list() forwards the scope query parameter', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse([{ id: 'w_1' }], {
        total_count: 1,
        page_count: 1,
        current_page: 1,
        limit: 20,
        has_next_page: false,
        has_previous_page: false,
      }),
    );
    const page = await make(requestImpl).list({ scope: 'public', page: 1 });
    expect(page).toBeInstanceOf(Page);
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/workflows',
      query: { page: 1, limit: undefined, search: undefined, sort: undefined, scope: 'public' },
    });
  });

  it('create() POSTs /workflows', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ id: 'w_1', name: 'Triage' }));
    const body = { name: 'Triage', system_prompt: 'You triage support requests.' };
    const w = await make(requestImpl).create(body, { idempotencyKey: 'op-1' });
    expect(w.id).toBe('w_1');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/workflows',
      body,
      idempotencyKey: 'op-1',
    });
  });

  it('clone() POSTs /workflows/clone with the source workflow id', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ id: 'w_2', name: 'Triage copy' }));
    const w = await make(requestImpl).clone(
      { source_workflow_id: 'w_1' },
      { idempotencyKey: 'op-1' },
    );
    expect(w.id).toBe('w_2');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/workflows/clone',
      body: { source_workflow_id: 'w_1' },
      idempotencyKey: 'op-1',
    });
  });

  it('retrieve() GETs /workflows/{id}', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ id: 'w_1' }));
    await make(requestImpl).retrieve('w_1');
    expect(requestImpl).toHaveBeenCalledWith({ method: 'GET', path: '/workflows/w_1' });
  });

  it('update() PATCHes /workflows/{id}', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ id: 'w_1' }));
    await make(requestImpl).update('w_1', { tags: ['v2'] });
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'PATCH',
      path: '/workflows/w_1',
      body: { tags: ['v2'] },
    });
  });

  it('delete() DELETEs /workflows/{id}', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse(null));
    await expect(make(requestImpl).delete('w_1')).resolves.toBeUndefined();
    expect(requestImpl).toHaveBeenCalledWith({ method: 'DELETE', path: '/workflows/w_1' });
  });
});
