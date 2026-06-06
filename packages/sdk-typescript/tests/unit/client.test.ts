import { describe, expect, it } from 'vitest';
import { BimpeAI } from '../../src/client';
import { UserError } from '../../src/core/errors';

describe('BimpeAI facade', () => {
  it('throws UserError when apiKey is missing', () => {
    expect(() => new BimpeAI({ apiKey: '' })).toThrow(UserError);
  });

  it('constructs successfully with apiKey', () => {
    const c = new BimpeAI({ apiKey: 'sk_test' });
    expect(c).toBeInstanceOf(BimpeAI);
  });

  it('exposes the raw request escape hatch', async () => {
    const fetchMock = async () =>
      new Response(JSON.stringify({ message: 'ok', data: null }), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      });
    const c = new BimpeAI({ apiKey: 'sk_test', fetch: fetchMock as unknown as typeof fetch });
    const res = await c.request({ method: 'GET', path: '/agents' });
    expect(res.data).toBeNull();
  });
});
