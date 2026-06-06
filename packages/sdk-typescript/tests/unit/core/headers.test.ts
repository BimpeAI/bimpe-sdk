import { describe, expect, it } from 'vitest';
import { mergeHeaders } from '../../../src/core/headers';

describe('mergeHeaders', () => {
  it('merges plain-object headers into a Headers instance', () => {
    const h = mergeHeaders({ 'Content-Type': 'application/json' }, { Accept: 'application/json' });
    expect(h.get('content-type')).toBe('application/json');
    expect(h.get('accept')).toBe('application/json');
  });

  it('is case-insensitive and last-write-wins', () => {
    const h = mergeHeaders(
      { 'content-type': 'text/plain' },
      { 'Content-Type': 'application/json' },
    );
    expect(h.get('content-type')).toBe('application/json');
  });

  it('accepts an existing Headers instance as input', () => {
    const a = new Headers({ Authorization: 'Bearer x' });
    const merged = mergeHeaders(a, { 'X-Custom': '1' });
    expect(merged.get('authorization')).toBe('Bearer x');
    expect(merged.get('x-custom')).toBe('1');
  });

  it('ignores undefined input slots', () => {
    const h = mergeHeaders(undefined, { Accept: 'application/json' }, undefined);
    expect(h.get('accept')).toBe('application/json');
  });
});
