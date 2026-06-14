export interface PaginationMeta {
  readonly total_count: number;
  readonly page_count: number;
  readonly current_page: number;
  readonly limit: number;
  readonly has_next_page: boolean;
  readonly has_previous_page: boolean;
}

export interface ListQuery {
  page?: number;
  limit?: number;
  search?: string;
  sort?: string;
}

export interface ApiResponse<T> {
  readonly data: T;
  readonly meta: PaginationMeta | null;
  readonly requestId: string | null;
  readonly status: number;
  readonly headers: Headers;
}

export interface ErrorBody {
  readonly message: string | readonly string[];
  readonly error?: string;
  readonly code?: string;
  readonly statusCode?: number;
  readonly request_id?: string;
}

export interface RequestOptions {
  idempotencyKey?: string;
  signal?: AbortSignal;
  timeout?: number;
  maxRetries?: number;
  headers?: Record<string, string>;
}

export interface InternalRequestSpec {
  method: 'GET' | 'POST' | 'PATCH' | 'DELETE' | 'PUT';
  path: string;
  query?: Record<string, string | number | boolean | undefined>;
  body?: unknown;
  headers?: Record<string, string>;
  signal?: AbortSignal;
  timeout?: number;
  maxRetries?: number;
  idempotencyKey?: string;
}

export type Fetch = typeof globalThis.fetch;

export interface Logger {
  debug(message: string, context?: Record<string, unknown>): void;
  warn(message: string, context?: Record<string, unknown>): void;
}

/**
 * The slice of the transport that resources depend on. Depending on this rather
 * than the concrete HttpClient keeps the transport class out of the public types.
 */
export interface RequestExecutor {
  request<T>(spec: InternalRequestSpec & RequestOptions): Promise<ApiResponse<T>>;
}

export interface StreamRequestSpec {
  path: string;
  query?: Record<string, string | number | boolean | undefined>;
  signal?: AbortSignal;
  headers?: Record<string, string>;
}

/**
 * Opens a long-lived response (Server-Sent Events) without bearer auth, envelope
 * unwrapping, or a request timeout. Returns the raw Response for the caller to read.
 */
export interface StreamExecutor {
  stream(spec: StreamRequestSpec): Promise<Response>;
}

export type Transport = RequestExecutor & StreamExecutor;
