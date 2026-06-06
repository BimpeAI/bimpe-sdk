import type { PaginationMeta } from './types';

export interface Unwrapped<T> {
  readonly data: T;
  readonly meta: PaginationMeta | null;
}

interface Envelope {
  message: string;
  data: unknown;
  meta?: PaginationMeta;
}

export function unwrapEnvelope<T>(body: unknown): Unwrapped<T> {
  if (!isEnvelope(body)) {
    throw new TypeError('Response is not a BimpeAI envelope (missing `message` field)');
  }
  return {
    data: body.data as T,
    meta: body.meta ?? null,
  };
}

function isEnvelope(value: unknown): value is Envelope {
  return (
    typeof value === 'object' &&
    value !== null &&
    'message' in value &&
    typeof (value as { message: unknown }).message === 'string'
  );
}
