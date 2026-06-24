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

describe('Agents integrations.bimpeai sub-resource', () => {
  it('bimpeai.list() GETs /agents/{id}/integrations/bimpeai', async () => {
    const requestImpl = vi
      .fn()
      .mockResolvedValue(
        okResponse([
          { id: 'ch_1', type: 'stripe', name: 'Stripe', status: 'enabled', is_connected: true },
        ]),
      );
    const out = await makeAgents(requestImpl).integrations.bimpeai.list('a_1');
    expect(out[0]?.type).toBe('stripe');
    expect(out[0]?.is_connected).toBe(true);
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/agents/a_1/integrations/bimpeai',
    });
  });

  it('bimpeai.configure() POSTs /configure with body and returns onboarding_url', async () => {
    const requestImpl = vi
      .fn()
      .mockResolvedValue(okResponse({ onboarding_url: 'https://agent.bimpe.ai/connect' }));
    const out = await makeAgents(requestImpl).integrations.bimpeai.configure(
      'a_1',
      { type: 'stripe', public_key: 'pk', secret_key: 'sk', currency: 'NGN' },
      { idempotencyKey: 'op-1' },
    );
    expect(out.onboarding_url).toBe('https://agent.bimpe.ai/connect');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/integrations/bimpeai/configure',
      body: { type: 'stripe', public_key: 'pk', secret_key: 'sk', currency: 'NGN' },
      idempotencyKey: 'op-1',
    });
  });

  it('bimpeai.disconnect() DELETEs /integrations/bimpeai/{id}', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse(null));
    await makeAgents(requestImpl).integrations.bimpeai.disconnect('a_1', 'ch_1');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'DELETE',
      path: '/agents/a_1/integrations/bimpeai/ch_1',
    });
  });
});

describe('Agents getTestCode', () => {
  it('getTestCode() GETs /agents/{id}/deployment/agent-test-code', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        code: 'ABC123XY',
        channels: {
          whatsapp: { is_enabled: true, start_message: 'start ABC123XY' },
          instagram: { is_enabled: true, start_message: 'start ABC123XY' },
          messenger: { is_enabled: false, start_message: 'start ABC123XY' },
          telephony: { is_enabled: true },
        },
      }),
    );
    const out = await makeAgents(requestImpl).getTestCode('a_1');
    expect(out.code).toBe('ABC123XY');
    expect(out.channels.whatsapp.is_enabled).toBe(true);
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/agents/a_1/deployment/agent-test-code',
    });
  });
});

describe('Agents integrations custom_api / mcp_server / pipedream', () => {
  it('customApi.configure() POSTs /custom_api/configure', async () => {
    const requestImpl = vi
      .fn()
      .mockResolvedValue(okResponse({ id: 'ci_1', config: { name: 'Shop', auth_type: 'none' } }));
    const out = await makeAgents(requestImpl).integrations.customApi.configure('a_1', {
      name: 'Shop',
      base_url: 'https://api.example.com',
    });
    expect(out.id).toBe('ci_1');
    expect(out.config.name).toBe('Shop');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/integrations/custom_api/configure',
      body: { name: 'Shop', base_url: 'https://api.example.com' },
    });
  });

  it('customApi.tools.add() POSTs /custom_api/{id}/tools', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        id: 't_1',
        action_name: 'create_order',
        name: 'Create Order',
        description: null,
        category: 'custom',
        is_enabled: true,
      }),
    );
    const out = await makeAgents(requestImpl).integrations.customApi.tools.add('a_1', 'ci_1', {
      name: 'Create Order',
      http_method: 'POST',
      url_template: '/orders',
    });
    expect(out.action_name).toBe('create_order');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/integrations/custom_api/ci_1/tools',
      body: { name: 'Create Order', http_method: 'POST', url_template: '/orders' },
    });
  });

  it('customApi.tools.delete() DELETEs the tool', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse(null));
    await makeAgents(requestImpl).integrations.customApi.tools.delete('a_1', 'ci_1', 't_1');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'DELETE',
      path: '/agents/a_1/integrations/custom_api/ci_1/tools/t_1',
    });
  });

  it('mcpServer.configure() POSTs and discover()/test() hit their endpoints', async () => {
    const cfg = vi.fn().mockResolvedValue(
      okResponse({
        id: 'm_1',
        config: {
          name: 'MR',
          server_url: 'https://x',
          transport: 'streamable_http',
          auth_type: 'none',
        },
      }),
    );
    const created = await makeAgents(cfg).integrations.mcpServer.configure('a_1', {
      name: 'MR',
      server_url: 'https://x',
    });
    expect(created.config.transport).toBe('streamable_http');

    const disc = vi
      .fn()
      .mockResolvedValue(okResponse({ discovered: 3, created: 2, updated: 1, disabled: 0 }));
    const result = await makeAgents(disc).integrations.mcpServer.discover('a_1', 'm_1');
    expect(result.discovered).toBe(3);
    expect(disc).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/integrations/mcp_server/m_1/discover',
    });

    const test = vi.fn().mockResolvedValue(okResponse({ success: true, message: 'ok' }));
    const t = await makeAgents(test).integrations.mcpServer.test('a_1', 'm_1');
    expect(t.success).toBe(true);
    expect(test).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/integrations/mcp_server/m_1/test',
    });
  });

  it('pipedream.configure() returns onboarding_url; disconnect DELETEs', async () => {
    const cfg = vi
      .fn()
      .mockResolvedValue(okResponse({ onboarding_url: 'https://agent.bimpe.ai/connect' }));
    const out = await makeAgents(cfg).integrations.pipedream.configure('a_1', {
      app_slug: 'google-sheets',
    });
    expect(out.onboarding_url).toContain('connect');
    expect(cfg).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/integrations/pipedream/configure',
      body: { app_slug: 'google-sheets' },
    });

    const del = vi.fn().mockResolvedValue(okResponse(null));
    await makeAgents(del).integrations.pipedream.disconnect('a_1', 'p_1');
    expect(del).toHaveBeenCalledWith({
      method: 'DELETE',
      path: '/agents/a_1/integrations/pipedream/p_1',
    });
  });
});
