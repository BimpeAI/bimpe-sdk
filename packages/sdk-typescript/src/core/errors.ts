import type { ErrorBody } from './types';

/** Known `code` values the API returns in an error envelope. */
export type ErrorCode =
  | 'validation_error'
  | 'bad_request'
  | 'unauthorized'
  | 'api_key_missing'
  | 'api_key_invalid'
  | 'api_key_expired'
  | 'insufficient_scope'
  | 'forbidden'
  | 'not_found'
  | 'conflict'
  | 'rate_limited'
  | 'too_many_requests'
  | 'not_implemented'
  | 'agent_limit_reached'
  | 'internal_error';

export class BimpeAIError extends Error {
  constructor(message: string) {
    super(message);
    this.name = new.target.name;
  }
}

export class UserError extends BimpeAIError {}

export class ConnectionError extends BimpeAIError {
  override readonly cause?: unknown;
  constructor(message: string, cause?: unknown) {
    super(message);
    this.cause = cause;
  }
}

export class ConnectionTimeoutError extends ConnectionError {}

export interface ApiErrorInit {
  message: string;
  status: number;
  code: string | null;
  requestId: string | null;
  headers: Headers;
  body: unknown;
}

export class ApiError extends BimpeAIError {
  readonly status: number;
  readonly code: string | null;
  readonly requestId: string | null;
  readonly headers: Headers;
  readonly body: unknown;

  constructor(init: ApiErrorInit) {
    super(init.message);
    this.status = init.status;
    this.code = init.code;
    this.requestId = init.requestId;
    this.headers = init.headers;
    this.body = init.body;
  }
}

export class BadRequestError extends ApiError {}

export interface FieldError {
  readonly path: string;
  readonly message: string;
}

export interface ValidationErrorInit extends ApiErrorInit {
  fieldErrors: readonly FieldError[];
}

export class ValidationError extends BadRequestError {
  readonly fieldErrors: readonly FieldError[];
  constructor(init: ValidationErrorInit) {
    super(init);
    this.fieldErrors = init.fieldErrors;
  }
}

export class AuthenticationError extends ApiError {}
export class PermissionDeniedError extends ApiError {}
export class NotFoundError extends ApiError {}
export class ConflictError extends ApiError {}

export interface RateLimitErrorInit extends ApiErrorInit {
  retryAfter?: number | null;
  limit?: number | null;
  remaining?: number | null;
  resetAt?: Date | null;
}

export class RateLimitError extends ApiError {
  readonly retryAfter: number | null;
  readonly limit: number | null;
  readonly remaining: number | null;
  readonly resetAt: Date | null;
  constructor(init: RateLimitErrorInit) {
    super(init);
    this.retryAfter = init.retryAfter ?? null;
    this.limit = init.limit ?? null;
    this.remaining = init.remaining ?? null;
    this.resetAt = init.resetAt ?? null;
  }
}

export class InternalServerError extends ApiError {}
export class NotImplementedError extends ApiError {}

export function mapApiError(status: number, body: unknown, headers: Headers): ApiError {
  const errBody = (body ?? {}) as ErrorBody;
  const message = normaliseMessage(errBody.message) ?? `HTTP ${status}`;
  const code = errBody.code ?? null;
  const requestId = headers.get('x-request-id') ?? errBody.request_id ?? null;
  const init: ApiErrorInit = { message, status, code, requestId, headers, body };

  if (status === 400) {
    if (code === 'validation_error') {
      return new ValidationError({ ...init, fieldErrors: parseFieldErrors(errBody.message) });
    }
    return new BadRequestError(init);
  }
  if (status === 401) return new AuthenticationError(init);
  if (status === 403) return new PermissionDeniedError(init);
  if (status === 404) return new NotFoundError(init);
  if (status === 409) return new ConflictError(init);
  if (status === 429) {
    return new RateLimitError({
      ...init,
      retryAfter: parseRetryAfter(headers.get('retry-after')),
      limit: numOrNull(headers.get('x-ratelimit-limit')),
      remaining: numOrNull(headers.get('x-ratelimit-remaining')),
      resetAt: parseReset(headers.get('x-ratelimit-reset')),
    });
  }
  if (status === 501) return new NotImplementedError(init);
  if (status >= 500) return new InternalServerError(init);
  return new ApiError(init);
}

function normaliseMessage(m: ErrorBody['message']): string | null {
  if (Array.isArray(m)) return m.join('; ');
  if (typeof m === 'string') return m;
  return null;
}

function parseFieldErrors(m: ErrorBody['message']): FieldError[] {
  if (!Array.isArray(m)) return [];
  const out: FieldError[] = [];
  for (const entry of m) {
    if (typeof entry !== 'string') continue;
    const idx = entry.indexOf(':');
    if (idx === -1) out.push({ path: '', message: entry });
    else out.push({ path: entry.slice(0, idx).trim(), message: entry.slice(idx + 1).trim() });
  }
  return out;
}

function parseRetryAfter(raw: string | null): number | null {
  if (!raw) return null;
  const asNumber = Number(raw);
  if (Number.isFinite(asNumber)) return Math.max(0, Math.floor(asNumber));
  const asDate = Date.parse(raw);
  if (Number.isFinite(asDate)) return Math.max(0, Math.ceil((asDate - Date.now()) / 1000));
  return null;
}

function parseReset(raw: string | null): Date | null {
  if (!raw) return null;
  const seconds = Number(raw);
  if (!Number.isFinite(seconds)) return null;
  return new Date(seconds * 1000);
}

function numOrNull(raw: string | null): number | null {
  if (raw === null) return null;
  const n = Number(raw);
  return Number.isFinite(n) ? n : null;
}
