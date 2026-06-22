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
    const body = {
      workflow_id: 'wf_1',
      name: 'Hello',
      description: 'A support agent',
      persona: 'friendly' as const,
    };
    const requestImpl = vi
      .fn()
      .mockResolvedValue(okResponse({ id: 'a_1', name: 'Hello', workflow: { id: 'wf_1' } }));
    const agent = await makeAgents(requestImpl).create(body, { idempotencyKey: 'op-1' });
    expect(agent.id).toBe('a_1');
    expect(agent.workflow?.id).toBe('wf_1');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents',
      body,
      idempotencyKey: 'op-1',
    });
  });

  it('retrieve() GETs /agents/{id} and returns the detail shape', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        id: 'a_1',
        name: 'Hello',
        knowledge_bases: [{ id: 'k_1', type: 'text', name: 'FAQ', description: null }],
        integrations: [
          { id: 'i_1', type: 'slack', name: 'Slack', status: 'active', is_connected: true },
        ],
        channels: [
          { id: 'c_1', type: 'whatsapp', name: 'WhatsApp', status: 'active', is_connected: true },
        ],
      }),
    );
    const detail = await makeAgents(requestImpl).retrieve('a_1');
    expect(detail.id).toBe('a_1');
    expect(detail.knowledge_bases[0]?.id).toBe('k_1');
    expect(detail.integrations[0]?.type).toBe('slack');
    expect(detail.channels[0]?.type).toBe('whatsapp');
    expect(requestImpl).toHaveBeenCalledWith({ method: 'GET', path: '/agents/a_1' });
  });

  it('updateLiveStatus() PATCHes /agents/{id}/live-status with body', async () => {
    const requestImpl = vi
      .fn()
      .mockResolvedValue(okResponse({ status: 'live', status_reason: 'launched' }));
    const status = await makeAgents(requestImpl).updateLiveStatus('a_1', {
      status: 'live',
      status_reason: 'launched',
    });
    expect(status.status).toBe('live');
    expect(status.status_reason).toBe('launched');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'PATCH',
      path: '/agents/a_1/live-status',
      body: { status: 'live', status_reason: 'launched' },
    });
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
