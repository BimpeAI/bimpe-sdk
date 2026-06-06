import { describe, expect, it } from 'vitest';
import { generateRequestId } from '../../../src/core/request-id';

const UUID_V4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

describe('generateRequestId', () => {
  it('produces a valid UUID v4 string', () => {
    expect(generateRequestId()).toMatch(UUID_V4);
  });

  it('produces unique values across many calls', () => {
    const set = new Set<string>();
    for (let i = 0; i < 1000; i += 1) set.add(generateRequestId());
    expect(set.size).toBe(1000);
  });
});
