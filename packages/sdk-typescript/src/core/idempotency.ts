import { generateRequestId } from './request-id';

export interface ResolveIdempotencyArgs {
  supplied: string | undefined;
  maxRetries: number;
}

export function resolveIdempotencyKey({
  supplied,
  maxRetries,
}: ResolveIdempotencyArgs): string | null {
  if (supplied) return supplied;
  if (maxRetries > 0) return generateRequestId();
  return null;
}
