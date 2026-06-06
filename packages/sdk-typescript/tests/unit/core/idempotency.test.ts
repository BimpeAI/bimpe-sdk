import { describe, expect, it } from 'vitest';
import { resolveIdempotencyKey } from '../../../src/core/idempotency';

const UUID_V4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

describe('resolveIdempotencyKey', () => {
  it('returns the caller-supplied key when provided', () => {
    expect(resolveIdempotencyKey({ supplied: 'op-1', maxRetries: 2 })).toBe('op-1');
  });

  it('auto-generates a UUID v4 when retries are on and no key supplied', () => {
    const key = resolveIdempotencyKey({ supplied: undefined, maxRetries: 2 });
    expect(key).toMatch(UUID_V4);
  });

  it('returns null when retries are off and no key supplied', () => {
    expect(resolveIdempotencyKey({ supplied: undefined, maxRetries: 0 })).toBeNull();
  });

  it('honors supplied key even when retries are off', () => {
    expect(resolveIdempotencyKey({ supplied: 'op-2', maxRetries: 0 })).toBe('op-2');
  });
});
