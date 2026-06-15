import { describe, expect, it } from 'vitest';
import type { ErrorCode } from '../../../src/core/errors';
import {
  ApiError,
  AuthenticationError,
  BadRequestError,
  BimpeAIError,
  ConflictError,
  ConnectionError,
  ConnectionTimeoutError,
  InternalServerError,
  NotFoundError,
  NotImplementedError,
  PermissionDeniedError,
  RateLimitError,
  UserError,
  ValidationError,
  mapApiError,
} from '../../../src/core/errors';

const h = (init: Record<string, string> = {}) => new Headers(init);

describe('error class hierarchy', () => {
  const apiInit = {
    message: 'x',
    status: 500,
    code: null,
    requestId: null,
    headers: h(),
    body: {},
  };

  it('all errors derive from BimpeAIError with a matching name', () => {
    const instances: [BimpeAIError, string][] = [
      [new UserError('x'), 'UserError'],
      [new ConnectionError('x'), 'ConnectionError'],
      [new ConnectionTimeoutError('x'), 'ConnectionTimeoutError'],
      [new ApiError(apiInit), 'ApiError'],
      [new BadRequestError(apiInit), 'BadRequestError'],
      [
        new ValidationError({ ...apiInit, status: 400, code: 'validation_error', fieldErrors: [] }),
        'ValidationError',
      ],
      [new AuthenticationError(apiInit), 'AuthenticationError'],
      [new PermissionDeniedError(apiInit), 'PermissionDeniedError'],
      [new NotFoundError(apiInit), 'NotFoundError'],
      [new ConflictError(apiInit), 'ConflictError'],
      [new RateLimitError({ ...apiInit, status: 429 }), 'RateLimitError'],
      [new InternalServerError(apiInit), 'InternalServerError'],
      [new NotImplementedError(apiInit), 'NotImplementedError'],
    ];
    for (const [inst, name] of instances) {
      expect(inst).toBeInstanceOf(BimpeAIError);
      expect(inst.name).toBe(name);
    }
  });
});

describe('mapApiError', () => {
  it('maps 400 + code=validation_error to ValidationError with parsed fieldErrors', () => {
    const err = mapApiError(
      400,
      { message: ['name: required', 'limit: too high'], code: 'validation_error' },
      h(),
    );
    expect(err).toBeInstanceOf(ValidationError);
    expect((err as ValidationError).fieldErrors).toEqual([
      { path: 'name', message: 'required' },
      { path: 'limit', message: 'too high' },
    ]);
  });

  it('maps 400 (other code) to BadRequestError', () => {
    const err = mapApiError(400, { message: 'bad', code: 'bad_request' }, h());
    expect(err).toBeInstanceOf(BadRequestError);
    expect(err).not.toBeInstanceOf(ValidationError);
  });

  it('maps 401 to AuthenticationError', () => {
    const err = mapApiError(401, { message: 'no key', code: 'api_key_missing' }, h());
    expect(err).toBeInstanceOf(AuthenticationError);
    expect(err.code).toBe('api_key_missing');
  });

  it('maps 403 to PermissionDeniedError', () => {
    const err = mapApiError(403, { message: 'denied', code: 'insufficient_scope' }, h());
    expect(err).toBeInstanceOf(PermissionDeniedError);
  });

  it('maps 404 to NotFoundError', () => {
    const err = mapApiError(404, { message: 'missing' }, h());
    expect(err).toBeInstanceOf(NotFoundError);
  });

  it('maps 409 to ConflictError', () => {
    const err = mapApiError(409, { message: 'conflict' }, h());
    expect(err).toBeInstanceOf(ConflictError);
  });

  it('maps 429 with code too_many_requests to RateLimitError and preserves the code', () => {
    const err = mapApiError(429, { message: 'too many', code: 'too_many_requests' }, h());
    expect(err).toBeInstanceOf(RateLimitError);
    expect(err.code).toBe('too_many_requests');
    const code: ErrorCode = 'too_many_requests';
    expect(code).toBe(err.code);
  });

  it('maps 429 to RateLimitError with parsed headers', () => {
    const err = mapApiError(
      429,
      { message: 'slow down' },
      h({
        'Retry-After': '7',
        'X-RateLimit-Limit': '60',
        'X-RateLimit-Remaining': '0',
        'X-RateLimit-Reset': '1700000000',
      }),
    ) as RateLimitError;
    expect(err).toBeInstanceOf(RateLimitError);
    expect(err.retryAfter).toBe(7);
    expect(err.limit).toBe(60);
    expect(err.remaining).toBe(0);
    expect(err.resetAt).toEqual(new Date(1700000000 * 1000));
  });

  it('parses Retry-After when given as an HTTP-date', () => {
    const future = new Date(Date.now() + 5000).toUTCString();
    const err = mapApiError(429, { message: 'x' }, h({ 'Retry-After': future })) as RateLimitError;
    expect(err.retryAfter).toBeGreaterThan(0);
    expect(err.retryAfter).toBeLessThanOrEqual(6);
  });

  it('maps 500 to InternalServerError', () => {
    expect(mapApiError(500, { message: 'oops' }, h())).toBeInstanceOf(InternalServerError);
  });

  it('maps 503 (unknown 5xx) to InternalServerError', () => {
    expect(mapApiError(503, { message: 'down' }, h())).toBeInstanceOf(InternalServerError);
  });

  it('maps 501 to NotImplementedError', () => {
    expect(mapApiError(501, { message: 'soon' }, h())).toBeInstanceOf(NotImplementedError);
  });

  it('falls back to ApiError for unknown status', () => {
    const err = mapApiError(418, { message: 'tea' }, h());
    expect(err).toBeInstanceOf(ApiError);
    expect(err).not.toBeInstanceOf(NotFoundError);
  });

  it('reads requestId from envelope.request_id when header is absent', () => {
    const err = mapApiError(500, { message: 'x', request_id: 'req_xyz' }, h());
    expect(err.requestId).toBe('req_xyz');
  });

  it('prefers X-Request-Id header over envelope.request_id', () => {
    const err = mapApiError(
      500,
      { message: 'x', request_id: 'req_body' },
      h({ 'X-Request-Id': 'req_header' }),
    );
    expect(err.requestId).toBe('req_header');
  });
});
