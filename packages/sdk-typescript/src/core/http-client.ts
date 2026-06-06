import { VERSION } from '../version';
import { unwrapEnvelope } from './envelope';
import {
  ApiError,
  BimpeAIError,
  ConnectionError,
  ConnectionTimeoutError,
  UserError,
  mapApiError,
} from './errors';
import { mergeHeaders } from './headers';
import { resolveIdempotencyKey } from './idempotency';
import { generateRequestId } from './request-id';
import { DEFAULT_BASE_MS, DEFAULT_MAX_BACKOFF_MS, computeBackoff, shouldRetry } from './retries';
import type { ApiResponse, Fetch, InternalRequestSpec, Logger, RequestOptions } from './types';

const DEFAULT_BASE_URL = 'https://api.bimpeai.com';
const API_PATH_PREFIX = '/api/v1/console';

export interface HttpClientConfig {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
  maxRetries?: number;
  fetch?: Fetch;
  defaultHeaders?: Record<string, string>;
  logger?: Logger;
}

export class HttpClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly timeout: number;
  private readonly maxRetries: number;
  private readonly fetchImpl: Fetch;
  private readonly defaultHeaders: Record<string, string>;
  private readonly logger: Logger | undefined;
  private readonly userAgent: string;

  constructor(config: HttpClientConfig) {
    if (!config.apiKey) throw new UserError('apiKey is required');
    this.apiKey = config.apiKey;
    this.baseUrl = (config.baseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, '');
    this.timeout = config.timeout ?? 30_000;
    this.maxRetries = config.maxRetries ?? 2;
    this.fetchImpl = config.fetch ?? globalThis.fetch.bind(globalThis);
    this.defaultHeaders = config.defaultHeaders ?? {};
    this.logger = config.logger;
    this.userAgent = buildUserAgent();
  }

  async request<T>(spec: InternalRequestSpec & RequestOptions): Promise<ApiResponse<T>> {
    const url = this.buildUrl(spec.path, spec.query);
    const maxRetries = spec.maxRetries ?? this.maxRetries;
    const timeout = spec.timeout ?? this.timeout;
    const idempotencyKey = isWrite(spec.method)
      ? resolveIdempotencyKey({ supplied: spec.idempotencyKey, maxRetries })
      : null;
    const requestId = readHeader(spec.headers, 'x-request-id') ?? generateRequestId();

    let attempt = 0;
    while (true) {
      try {
        return await this.send<T>(url, spec, idempotencyKey, requestId, timeout);
      } catch (error) {
        if (!shouldRetry(error, attempt, maxRetries)) throw error;
        const retryAfter =
          error instanceof ApiError
            ? parseRetryAfterMs(error.headers.get('retry-after'))
            : undefined;
        const delay = computeBackoff(attempt, DEFAULT_BASE_MS, DEFAULT_MAX_BACKOFF_MS, retryAfter);
        this.logger?.debug('retrying request', { attempt, delay, requestId });
        await sleep(delay);
        attempt += 1;
      }
    }
  }

  private async send<T>(
    url: string,
    spec: InternalRequestSpec & RequestOptions,
    idempotencyKey: string | null,
    requestId: string,
    timeout: number,
  ): Promise<ApiResponse<T>> {
    const headers = mergeHeaders(
      this.defaultHeaders,
      {
        Authorization: `Bearer ${this.apiKey}`,
        Accept: 'application/json',
        'User-Agent': this.userAgent,
        'X-Request-Id': requestId,
        ...(spec.body !== undefined ? { 'Content-Type': 'application/json' } : {}),
        ...(idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : {}),
      },
      spec.headers,
    );

    const controller = new AbortController();
    const timeoutHandle = setTimeout(
      () => controller.abort(new DOMException('timeout', 'TimeoutError')),
      timeout,
    );
    const { signal, cleanup } = composeSignals(controller.signal, spec.signal);

    let response: Response;
    try {
      response = await this.fetchImpl(url, {
        method: spec.method,
        headers,
        body: spec.body !== undefined ? JSON.stringify(spec.body) : null,
        signal,
      });
    } catch (cause) {
      if (isAbortError(cause)) {
        if (controller.signal.aborted) throw new ConnectionTimeoutError('request timed out', cause);
        throw new ConnectionError('request aborted', cause);
      }
      throw new ConnectionError('network error', cause);
    } finally {
      clearTimeout(timeoutHandle);
      cleanup();
    }

    const text = await response.text();
    const parsed = text.length ? safeJson(text) : null;

    if (!response.ok) {
      throw mapApiError(response.status, parsed, response.headers);
    }

    let unwrapped: { data: T; meta: ApiResponse<T>['meta'] };
    try {
      unwrapped = unwrapEnvelope<T>(parsed);
    } catch {
      throw new BimpeAIError(
        `Expected a BimpeAI response envelope but got an unrecognised body (status ${response.status})`,
      );
    }

    return {
      data: unwrapped.data,
      meta: unwrapped.meta,
      requestId: response.headers.get('x-request-id') ?? requestId,
      status: response.status,
      headers: response.headers,
    };
  }

  private buildUrl(path: string, query?: InternalRequestSpec['query']): string {
    const url = new URL(`${this.baseUrl}${API_PATH_PREFIX}${path}`);
    if (query) {
      for (const [key, value] of Object.entries(query)) {
        if (value === undefined) continue;
        url.searchParams.set(key, String(value));
      }
    }
    return url.toString();
  }
}

function buildUserAgent(): string {
  const runtime = detectRuntime();
  const platform =
    typeof process !== 'undefined' ? `${process.platform}/${process.arch}` : 'unknown';
  return `bimpeai-sdk-typescript/${VERSION} (${runtime}; ${platform})`;
}

function detectRuntime(): string {
  const g = globalThis as {
    Bun?: { version: string };
    Deno?: { version: { deno: string } };
  };
  if (typeof g.Bun !== 'undefined') return `Bun/${g.Bun.version}`;
  if (typeof g.Deno !== 'undefined') return `Deno/${g.Deno.version.deno}`;
  if (typeof process !== 'undefined' && process.versions?.node)
    return `Node/${process.versions.node}`;
  return 'Browser';
}

function isWrite(method: string): boolean {
  return method === 'POST' || method === 'PATCH' || method === 'PUT' || method === 'DELETE';
}

function readHeader(headers: Record<string, string> | undefined, name: string): string | undefined {
  if (!headers) return undefined;
  const lower = name.toLowerCase();
  for (const [key, value] of Object.entries(headers)) {
    if (key.toLowerCase() === lower) return value;
  }
  return undefined;
}

function isAbortError(e: unknown): boolean {
  return (
    typeof e === 'object' &&
    e !== null &&
    'name' in e &&
    ((e as { name: string }).name === 'AbortError' ||
      (e as { name: string }).name === 'TimeoutError')
  );
}

interface ComposedSignal {
  signal: AbortSignal;
  cleanup: () => void;
}

function composeSignals(a: AbortSignal, b?: AbortSignal): ComposedSignal {
  const noop = () => {};
  if (!b) return { signal: a, cleanup: noop };

  const anyFn = (AbortSignal as { any?: (signals: AbortSignal[]) => AbortSignal }).any;
  if (typeof anyFn === 'function') return { signal: anyFn([a, b]), cleanup: noop };

  const ctrl = new AbortController();
  const onA = () => ctrl.abort(a.reason);
  const onB = () => ctrl.abort(b.reason);
  if (a.aborted) ctrl.abort(a.reason);
  else a.addEventListener('abort', onA, { once: true });
  if (b.aborted) ctrl.abort(b.reason);
  else b.addEventListener('abort', onB, { once: true });

  const cleanup = () => {
    a.removeEventListener('abort', onA);
    b.removeEventListener('abort', onB);
  };
  return { signal: ctrl.signal, cleanup };
}

function safeJson(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function parseRetryAfterMs(raw: string | null): number | undefined {
  if (!raw || !raw.trim()) return undefined;
  const seconds = Number(raw);
  if (Number.isFinite(seconds)) return Math.max(0, Math.floor(seconds)) * 1000;
  const asDate = Date.parse(raw);
  if (Number.isFinite(asDate)) return Math.max(0, asDate - Date.now());
  return undefined;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
