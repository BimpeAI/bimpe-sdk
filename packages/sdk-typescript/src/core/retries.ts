import {
  ApiError,
  BimpeAIError,
  ConflictError,
  ConnectionError,
  ConnectionTimeoutError,
  NotImplementedError,
} from './errors';

export const DEFAULT_BASE_MS = 500;
export const DEFAULT_MAX_BACKOFF_MS = 8000;

const RETRYABLE_STATUSES = new Set([408, 429]);

export function shouldRetry(error: unknown, attempt: number, maxRetries: number): boolean {
  if (attempt >= maxRetries) return false;
  if (!(error instanceof BimpeAIError)) return false;
  if (error instanceof ConnectionTimeoutError || error instanceof ConnectionError) return true;
  if (error instanceof NotImplementedError) return false;
  if (error instanceof ConflictError) return false;
  if (error instanceof ApiError) {
    if (RETRYABLE_STATUSES.has(error.status)) return true;
    if (error.status >= 500 && error.status !== 501) return true;
  }
  return false;
}

export function computeBackoff(
  attempt: number,
  baseMs: number = DEFAULT_BASE_MS,
  maxMs: number = DEFAULT_MAX_BACKOFF_MS,
  retryAfterMs?: number,
): number {
  if (typeof retryAfterMs === 'number' && retryAfterMs >= 0) {
    return Math.min(retryAfterMs, maxMs);
  }
  const exponential = Math.min(maxMs, baseMs * 2 ** attempt);
  const jitter = 0.5 + Math.random() * 0.5;
  return Math.floor(exponential * jitter);
}
