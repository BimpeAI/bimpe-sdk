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
          name: 'Slack',
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
    expect(requestImpl).toHaveBeenCalledWith({ method: 'GET', path: '/agents/a_1/actions' });
  });

  it('actions.enable() POSTs /agents/{id}/actions/enable', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ updated: 1 }));
    await makeAgents(requestImpl).actions.enable('a_1', { action_ids: ['ac_1'] });
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/actions/enable',
      body: { action_ids: ['ac_1'] },
    });
  });

  it('actions.disable() POSTs /agents/{id}/actions/disable', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ updated: 1 }));
    await makeAgents(requestImpl).actions.disable('a_1', { action_ids: ['ac_1'] });
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/actions/disable',
      body: { action_ids: ['ac_1'] },
    });
  });
});
