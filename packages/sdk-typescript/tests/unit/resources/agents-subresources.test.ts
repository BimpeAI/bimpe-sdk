import { describe, expect, it, vi } from 'vitest';
import { Agents } from '../../../src/resources/agents/agents';

const okResponse = <T>(data: T) => ({
  data,
  meta: null,
  requestId: 'r1',
  status: 200,
  headers: new Headers(),
});

const makeAgents = (requestImpl: ReturnType<typeof vi.fn>) =>
  new Agents({ request: requestImpl } as never);

describe('Agents read-only sub-resources', () => {
  it('integrations.list() GETs /agents/{id}/integrations', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse([
        {
          id: 'i_1',
          type: 'slack',
          status: 'active',
          is_connected: true,
          config_fields: [],
          actions: [],
        },
      ]),
    );
    const out = await makeAgents(requestImpl).integrations.list('a_1');
    expect(out[0]?.type).toBe('slack');
    expect(requestImpl).toHaveBeenCalledWith({ method: 'GET', path: '/agents/a_1/integrations' });
  });

  it('channels.list() GETs /agents/{id}/channels', async () => {
    const requestImpl = vi
      .fn()
      .mockResolvedValue(
        okResponse([
          { id: 'c_1', type: 'whatsapp', name: 'WhatsApp', status: 'active', is_connected: true },
        ]),
      );
    const out = await makeAgents(requestImpl).channels.list('a_1');
    expect(out[0]?.type).toBe('whatsapp');
    expect(out[0]?.name).toBe('WhatsApp');
    expect(requestImpl).toHaveBeenCalledWith({ method: 'GET', path: '/agents/a_1/channels' });
  });

  it('actions.list() GETs /agents/{id}/actions', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse([
        {
          id: 'ac_1',
          integration_id: 'i_1',
          integration_type: 'slack',
          integration_name: 'Slack',
          name: 'Post',
          action_name: 'slack_post',
          description: null,
          is_enabled: true,
        },
      ]),
    );
    const out = await makeAgents(requestImpl).actions.list('a_1');
    expect(out[0]?.action_name).toBe('slack_post');
    expect(out[0]?.integration_id).toBe('i_1');
    expect(requestImpl).toHaveBeenCalledWith({ method: 'GET', path: '/agents/a_1/actions' });
  });

  it('actions.enable() POSTs /agents/{id}/actions/enable and returns updated_count', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ updated_count: 2 }));
    const out = await makeAgents(requestImpl).actions.enable('a_1', {
      action_ids: ['ac_1', 'ac_2'],
    });
    expect(out.updated_count).toBe(2);
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/actions/enable',
      body: { action_ids: ['ac_1', 'ac_2'] },
    });
  });

  it('actions.disable() POSTs /agents/{id}/actions/disable and returns updated_count', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ updated_count: 1 }));
    const out = await makeAgents(requestImpl).actions.disable('a_1', { action_ids: ['ac_1'] });
    expect(out.updated_count).toBe(1);
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/actions/disable',
      body: { action_ids: ['ac_1'] },
    });
  });
});
