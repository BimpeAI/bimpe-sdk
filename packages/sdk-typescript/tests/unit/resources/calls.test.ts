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
});
