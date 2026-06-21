import { describe, expect, it, vi } from 'vitest';
import { NotImplementedError } from '../../../src/core/errors';
import { Calls } from '../../../src/resources/calls/calls';

describe('Calls resource', () => {
  it('list() surfaces the upstream NotImplementedError and hits GET /calls', async () => {
    const requestImpl = vi.fn().mockRejectedValue(
      new NotImplementedError({
        message: 'coming soon',
        status: 501,
        code: 'not_implemented',
        requestId: null,
        headers: new Headers(),
        body: {},
      }),
    );
    const calls = new Calls({ request: requestImpl } as never);
    await expect(calls.list()).rejects.toBeInstanceOf(NotImplementedError);
    expect(requestImpl).toHaveBeenCalledWith({ method: 'GET', path: '/calls' });
  });

  it('make() POSTs /calls', async () => {
    const requestImpl = vi.fn().mockResolvedValue({
      data: { agent_id: 'a_1' },
      meta: null,
      requestId: 'r1',
      status: 200,
      headers: new Headers(),
    });
    const out = await new Calls({ request: requestImpl } as never).make({ agent_id: 'a_1' });
    expect(out).toEqual({ agent_id: 'a_1' });
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/calls',
      body: { agent_id: 'a_1' },
    });
  });

  it('queue() POSTs /calls/queue', async () => {
    const requestImpl = vi.fn().mockResolvedValue({
      data: { agent_id: 'a_1' },
      meta: null,
      requestId: 'r1',
      status: 200,
      headers: new Headers(),
    });
    await new Calls({ request: requestImpl } as never).queue({ agent_id: 'a_1' });
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/calls/queue',
      body: { agent_id: 'a_1' },
    });
  });
});
