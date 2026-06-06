import { describe, expect, it } from 'vitest';
import {
  ApiError,
  ConflictError,
  ConnectionError,
  ConnectionTimeoutError,
  InternalServerError,
  NotFoundError,
  NotImplementedError,
  RateLimitError,
} from '../../../src/core/errors';
import {
  DEFAULT_BASE_MS,
  DEFAULT_MAX_BACKOFF_MS,
  computeBackoff,
  shouldRetry,
} from '../../../src/core/retries';

const h = () => new Headers();
const apiError = (status: number) =>
  new ApiError({ message: 'x', status, code: null, requestId: null, headers: h(), body: {} });

describe('shouldRetry', () => {
  it('retries network errors', () => {
    expect(shouldRetry(new ConnectionError('econnreset'), 0, 2)).toBe(true);
  });

  it('retries timeouts', () => {
    expect(shouldRetry(new ConnectionTimeoutError('timeout'), 0, 2)).toBe(true);
  });

  it('retries 408, 429, and 5xx (except 501)', () => {
    expect(shouldRetry(apiError(408), 0, 2)).toBe(true);
    expect(
      shouldRetry(
        new RateLimitError({
          message: 'x',
          status: 429,
          code: null,
          requestId: null,
          headers: h(),
          body: {},
        }),
        0,
        2,
      ),
    ).toBe(true);
    expect(
      shouldRetry(
        new InternalServerError({
          message: 'x',
          status: 500,
          code: null,
          requestId: null,
          headers: h(),
          body: {},
        }),
        0,
        2,
      ),
    ).toBe(true);
    expect(shouldRetry(apiError(502), 0, 2)).toBe(true);
    expect(shouldRetry(apiError(503), 0, 2)).toBe(true);
  });

  it('does not retry 409', () => {
    const conflict = new ConflictError({
      message: 'x',
      status: 409,
      code: null,
      requestId: null,
      headers: h(),
      body: {},
    });
    expect(shouldRetry(conflict, 0, 2)).toBe(false);
  });

  it('does not retry 4xx other than 408/429', () => {
    expect(
      shouldRetry(
        new NotFoundError({
          message: 'x',
          status: 404,
          code: null,
          requestId: null,
          headers: h(),
          body: {},
        }),
        0,
        2,
      ),
    ).toBe(false);
    expect(shouldRetry(apiError(400), 0, 2)).toBe(false);
    expect(shouldRetry(apiError(401), 0, 2)).toBe(false);
    expect(shouldRetry(apiError(403), 0, 2)).toBe(false);
  });

  it('does not retry 501 (NotImplementedError)', () => {
    const ni = new NotImplementedError({
      message: 'x',
      status: 501,
      code: null,
      requestId: null,
      headers: h(),
      body: {},
    });
    expect(shouldRetry(ni, 0, 2)).toBe(false);
  });

  it('stops once attempt >= maxRetries', () => {
    expect(shouldRetry(apiError(500), 2, 2)).toBe(false);
    expect(shouldRetry(apiError(500), 1, 2)).toBe(true);
  });

  it('returns false when error is not a BimpeAI error', () => {
    expect(shouldRetry(new Error('random'), 0, 2)).toBe(false);
  });
});

describe('computeBackoff', () => {
  it('grows roughly exponentially across attempts', () => {
    const a = computeBackoff(0, 500, 8000);
    const b = computeBackoff(1, 500, 8000);
    const c = computeBackoff(2, 500, 8000);
    expect(a).toBeGreaterThan(0);
    expect(b).toBeGreaterThan(a);
    expect(c).toBeGreaterThan(b);
  });

  it('clamps at maxBackoff', () => {
    const d = computeBackoff(20, 500, 8000);
    expect(d).toBeLessThanOrEqual(8000);
  });

  it('honors retryAfterMs when supplied, clamped to maxBackoff', () => {
    expect(computeBackoff(0, 500, 8000, 3000)).toBe(3000);
    expect(computeBackoff(0, 500, 8000, 20_000)).toBe(8000);
  });

  it('uses sensible defaults', () => {
    expect(DEFAULT_BASE_MS).toBe(500);
    expect(DEFAULT_MAX_BACKOFF_MS).toBe(8000);
  });
});
