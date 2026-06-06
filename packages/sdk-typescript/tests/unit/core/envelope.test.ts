import { describe, expect, it } from 'vitest';
import { unwrapEnvelope } from '../../../src/core/envelope';

describe('unwrapEnvelope', () => {
  it('unwraps a single-resource envelope', () => {
    const result = unwrapEnvelope<{ id: string }>({
      message: 'ok',
      data: { id: 'a_1' },
    });
    expect(result).toEqual({ data: { id: 'a_1' }, meta: null });
  });

  it('unwraps a paginated envelope', () => {
    const result = unwrapEnvelope<{ id: string }[]>({
      message: 'ok',
      data: [{ id: 'a_1' }],
      meta: {
        total_count: 1,
        page_count: 1,
        current_page: 1,
        limit: 20,
        has_next_page: false,
        has_previous_page: false,
      },
    });
    expect(result.data).toEqual([{ id: 'a_1' }]);
    expect(result.meta?.total_count).toBe(1);
  });

  it('unwraps a null-data envelope (DELETE)', () => {
    const result = unwrapEnvelope<null>({ message: 'deleted', data: null });
    expect(result).toEqual({ data: null, meta: null });
  });

  it('throws on a non-envelope shape', () => {
    expect(() => unwrapEnvelope<unknown>({ id: 'x' } as unknown)).toThrow(/envelope/i);
  });
});
