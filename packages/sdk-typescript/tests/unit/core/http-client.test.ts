import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  AuthenticationError,
  BimpeAIError,
  NotFoundError,
  RateLimitError,
  ValidationError,
} from '../../../src/core/errors';
import { HttpClient } from '../../../src/core/http-client';

const ok = (body: unknown, init: ResponseInit = {}) =>
  new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'content-type': 'application/json', ...(init.headers as Record<string, string>) },
    ...init,
  });

const err = (status: number, body: unknown, headers: Record<string, string> = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json', ...headers },
  });

describe('HttpClient — request construction', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchMock = vi.fn();
  });

  it('builds the URL from baseUrl + path + query', async () => {
    fetchMock.mockResolvedValueOnce(ok({ message: 'ok', data: { id: 'a' } }));
    const c = new HttpClient({
      apiKey: 'sk_test',
      baseUrl: 'https://api.example.com',
      fetch: fetchMock as unknown as typeof fetch,
    });
    await c.request({ method: 'GET', path: '/agents', query: { page: 2, search: 'hi' } });
    const url = new URL(fetchMock.mock.calls[0]?.[0] as string);
    expect(url.pathname).toBe('/api/v1/console/agents');
    expect(url.searchParams.get('page')).toBe('2');
    expect(url.searchParams.get('search')).toBe('hi');
  });

  it('omits undefined query values', async () => {
    fetchMock.mockResolvedValueOnce(ok({ message: 'ok', data: null }));
    const c = new HttpClient({ apiKey: 'sk_test', fetch: fetchMock as unknown as typeof fetch });
    await c.request({ method: 'GET', path: '/agents', query: { page: 1, search: undefined } });
    const url = new URL(fetchMock.mock.calls[0]?.[0] as string);
    expect(url.searchParams.has('search')).toBe(false);
  });

  it('sends Authorization: Bearer header', async () => {
    fetchMock.mockResolvedValueOnce(ok({ message: 'ok', data: null }));
    const c = new HttpClient({ apiKey: 'sk_secret', fetch: fetchMock as unknown as typeof fetch });
    await c.request({ method: 'GET', path: '/agents' });
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect((init.headers as Headers).get('authorization')).toBe('Bearer sk_secret');
  });

  it('throws UserError when apiKey is missing', () => {
    expect(
      () => new HttpClient({ apiKey: '', fetch: fetchMock as unknown as typeof fetch }),
    ).toThrow(/apiKey/i);
  });

  it('sends User-Agent', async () => {
    fetchMock.mockResolvedValueOnce(ok({ message: 'ok', data: null }));
    const c = new HttpClient({ apiKey: 'sk_test', fetch: fetchMock as unknown as typeof fetch });
    await c.request({ method: 'GET', path: '/agents' });
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect((init.headers as Headers).get('user-agent')).toMatch(/bimpeai-sdk-typescript\/\d/);
  });

  it('serialises JSON body and sets content-type', async () => {
    fetchMock.mockResolvedValueOnce(ok({ message: 'created', data: { id: 'a_1' } }));
    const c = new HttpClient({ apiKey: 'sk_test', fetch: fetchMock as unknown as typeof fetch });
    await c.request({ method: 'POST', path: '/agents', body: { name: 'A' } });
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect((init.headers as Headers).get('content-type')).toBe('application/json');
    expect(init.body).toBe(JSON.stringify({ name: 'A' }));
  });

  it('generates X-Request-Id when caller does not supply one', async () => {
    fetchMock.mockResolvedValueOnce(ok({ message: 'ok', data: null }));
    const c = new HttpClient({ apiKey: 'sk_test', fetch: fetchMock as unknown as typeof fetch });
    await c.request({ method: 'GET', path: '/agents' });
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect((init.headers as Headers).get('x-request-id')).toMatch(/^[0-9a-f-]{36}$/);
  });

  it('respects caller-supplied X-Request-Id via headers', async () => {
    fetchMock.mockResolvedValueOnce(ok({ message: 'ok', data: null }));
    const c = new HttpClient({ apiKey: 'sk_test', fetch: fetchMock as unknown as typeof fetch });
    await c.request({ method: 'GET', path: '/agents', headers: { 'X-Request-Id': 'req_caller' } });
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect((init.headers as Headers).get('x-request-id')).toBe('req_caller');
  });

  it('returns ApiResponse with unwrapped data, meta, requestId', async () => {
    fetchMock.mockResolvedValueOnce(
      ok(
        {
          message: 'ok',
          data: [{ id: 'a_1' }],
          meta: {
            total_count: 1,
            page_count: 1,
            current_page: 1,
            limit: 20,
            has_next_page: false,
            has_previous_page: false,
          },
        },
        { headers: { 'x-request-id': 'req_xyz' } },
      ),
    );
    const c = new HttpClient({ apiKey: 'sk_test', fetch: fetchMock as unknown as typeof fetch });
    const res = await c.request<{ id: string }[]>({ method: 'GET', path: '/agents' });
    expect(res.data).toEqual([{ id: 'a_1' }]);
    expect(res.meta?.total_count).toBe(1);
    expect(res.requestId).toBe('req_xyz');
    expect(res.status).toBe(200);
  });
});

describe('HttpClient — error mapping', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchMock = vi.fn();
  });

  it('throws AuthenticationError on 401', async () => {
    fetchMock.mockResolvedValueOnce(err(401, { message: 'no key', code: 'api_key_missing' }));
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      maxRetries: 0,
    });
    await expect(c.request({ method: 'GET', path: '/agents' })).rejects.toBeInstanceOf(
      AuthenticationError,
    );
  });

  it('throws NotFoundError on 404', async () => {
    fetchMock.mockResolvedValueOnce(err(404, { message: 'missing' }));
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      maxRetries: 0,
    });
    await expect(c.request({ method: 'GET', path: '/agents/x' })).rejects.toBeInstanceOf(
      NotFoundError,
    );
  });

  it('throws ValidationError on 400 + validation_error', async () => {
    fetchMock.mockResolvedValueOnce(
      err(400, { message: ['name: required'], code: 'validation_error' }),
    );
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      maxRetries: 0,
    });
    await expect(c.request({ method: 'POST', path: '/agents' })).rejects.toBeInstanceOf(
      ValidationError,
    );
  });

  it('throws RateLimitError on 429 with parsed metadata', async () => {
    fetchMock.mockResolvedValueOnce(
      err(
        429,
        { message: 'slow' },
        { 'retry-after': '1', 'x-ratelimit-limit': '60', 'x-ratelimit-remaining': '0' },
      ),
    );
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      maxRetries: 0,
    });
    const promise = c.request({ method: 'GET', path: '/agents' });
    await expect(promise).rejects.toBeInstanceOf(RateLimitError);
    await promise.catch((e: RateLimitError) => {
      expect(e.retryAfter).toBe(1);
      expect(e.limit).toBe(60);
    });
  });
});

describe('HttpClient — retries', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchMock = vi.fn();
  });

  it('retries on 500 and succeeds on the second attempt', async () => {
    fetchMock
      .mockResolvedValueOnce(err(500, { message: 'oops' }))
      .mockResolvedValueOnce(ok({ message: 'ok', data: null }));
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      maxRetries: 2,
    });
    const res = await c.request({ method: 'GET', path: '/agents' });
    expect(res.data).toBeNull();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it('does not retry on 400', async () => {
    fetchMock.mockResolvedValueOnce(err(400, { message: 'bad' }));
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      maxRetries: 2,
    });
    await expect(c.request({ method: 'GET', path: '/agents' })).rejects.toBeDefined();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('reuses the same Idempotency-Key across retries', async () => {
    fetchMock
      .mockResolvedValueOnce(err(500, { message: 'oops' }))
      .mockResolvedValueOnce(ok({ message: 'ok', data: { id: 'a_1' } }));
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      maxRetries: 2,
    });
    await c.request({
      method: 'POST',
      path: '/agents',
      body: { name: 'A' },
      idempotencyKey: 'op-1',
    });
    const key0 = (fetchMock.mock.calls[0]?.[1] as RequestInit).headers as Headers;
    const key1 = (fetchMock.mock.calls[1]?.[1] as RequestInit).headers as Headers;
    expect(key0.get('idempotency-key')).toBe('op-1');
    expect(key1.get('idempotency-key')).toBe('op-1');
  });

  it('auto-generates Idempotency-Key for POST when retries enabled and none supplied', async () => {
    fetchMock.mockResolvedValueOnce(ok({ message: 'ok', data: { id: 'a_1' } }));
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      maxRetries: 2,
    });
    await c.request({ method: 'POST', path: '/agents', body: { name: 'A' } });
    const headers = (fetchMock.mock.calls[0]?.[1] as RequestInit).headers as Headers;
    expect(headers.get('idempotency-key')).toMatch(/^[0-9a-f-]{36}$/);
  });

  it('does not auto-generate Idempotency-Key when maxRetries is 0', async () => {
    fetchMock.mockResolvedValueOnce(ok({ message: 'ok', data: { id: 'a_1' } }));
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      maxRetries: 0,
    });
    await c.request({ method: 'POST', path: '/agents', body: { name: 'A' } });
    const headers = (fetchMock.mock.calls[0]?.[1] as RequestInit).headers as Headers;
    expect(headers.get('idempotency-key')).toBeNull();
  });

  it('does not attach Idempotency-Key on GET', async () => {
    fetchMock.mockResolvedValueOnce(ok({ message: 'ok', data: null }));
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      maxRetries: 2,
    });
    await c.request({ method: 'GET', path: '/agents' });
    const headers = (fetchMock.mock.calls[0]?.[1] as RequestInit).headers as Headers;
    expect(headers.get('idempotency-key')).toBeNull();
  });
});

describe('HttpClient — timeout and abort', () => {
  it('aborts when client timeout elapses', async () => {
    const fetchMock = vi.fn(
      (_input: RequestInfo | URL, init?: RequestInit) =>
        new Promise<Response>((_resolve, reject) => {
          init?.signal?.addEventListener('abort', () =>
            reject(new DOMException('aborted', 'AbortError')),
          );
        }),
    );
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      timeout: 20,
      maxRetries: 0,
    });
    await expect(c.request({ method: 'GET', path: '/agents' })).rejects.toThrow(/timed out/i);
  });

  it('aborts when caller signal fires', async () => {
    const fetchMock = vi.fn(
      (_input: RequestInfo | URL, init?: RequestInit) =>
        new Promise<Response>((_resolve, reject) => {
          init?.signal?.addEventListener('abort', () =>
            reject(new DOMException('aborted', 'AbortError')),
          );
        }),
    );
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      maxRetries: 0,
    });
    const ac = new AbortController();
    queueMicrotask(() => ac.abort());
    await expect(c.request({ method: 'GET', path: '/agents', signal: ac.signal })).rejects.toThrow(
      /abort/i,
    );
  });
});

describe('HttpClient — request id and response shape', () => {
  it('reuses one X-Request-Id across retries', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(err(500, { message: 'oops' }))
      .mockResolvedValueOnce(ok({ message: 'ok', data: null }));
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      maxRetries: 2,
    });
    await c.request({ method: 'GET', path: '/agents' });
    const first = (fetchMock.mock.calls[0]?.[1] as RequestInit).headers as Headers;
    const second = (fetchMock.mock.calls[1]?.[1] as RequestInit).headers as Headers;
    expect(first.get('x-request-id')).toMatch(/^[0-9a-f-]{36}$/);
    expect(second.get('x-request-id')).toBe(first.get('x-request-id'));
  });

  it('falls back to the sent request id when the server does not echo one', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(ok({ message: 'ok', data: null }));
    const c = new HttpClient({ apiKey: 'sk_test', fetch: fetchMock as unknown as typeof fetch });
    const res = await c.request({ method: 'GET', path: '/agents' });
    const sent = ((fetchMock.mock.calls[0]?.[1] as RequestInit).headers as Headers).get(
      'x-request-id',
    );
    expect(res.requestId).toBe(sent);
  });

  it('throws a BimpeAIError on a 2xx body that is not an envelope', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(
      new Response(JSON.stringify([{ id: 'a_1' }]), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      }),
    );
    const c = new HttpClient({ apiKey: 'sk_test', fetch: fetchMock as unknown as typeof fetch });
    await expect(c.request({ method: 'GET', path: '/agents' })).rejects.toBeInstanceOf(
      BimpeAIError,
    );
  });
});

describe('HttpClient — stream', () => {
  const sseBody = () =>
    new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('event: message\ndata: {"id":"m_1"}\n\n'));
        controller.close();
      },
    });

  it('opens a GET stream with the event-stream Accept header and no bearer auth', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        new Response(sseBody(), { status: 200, headers: { 'content-type': 'text/event-stream' } }),
      );
    const c = new HttpClient({ apiKey: 'sk_test', fetch: fetchMock as unknown as typeof fetch });
    await c.stream({
      path: '/agents/a_1/conversations/cv_1/messages/stream',
      query: { ticket: 't1' },
    });
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(new URL(url).searchParams.get('ticket')).toBe('t1');
    expect(init.method).toBe('GET');
    const headers = init.headers as Headers;
    expect(headers.get('accept')).toBe('text/event-stream');
    expect(headers.get('authorization')).toBeNull();
    expect(headers.get('user-agent')).toMatch(/bimpeai-sdk-typescript/);
  });

  it('returns the raw Response so the body can be read', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        new Response(sseBody(), { status: 200, headers: { 'content-type': 'text/event-stream' } }),
      );
    const c = new HttpClient({ apiKey: 'sk_test', fetch: fetchMock as unknown as typeof fetch });
    const res = await c.stream({ path: '/x' });
    expect(res.body).toBeInstanceOf(ReadableStream);
  });

  it('maps a non-2xx open to a typed error', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ message: 'too many', code: 'too_many_requests' }), {
        status: 429,
        headers: { 'content-type': 'application/json' },
      }),
    );
    const c = new HttpClient({ apiKey: 'sk_test', fetch: fetchMock as unknown as typeof fetch });
    await expect(c.stream({ path: '/x' })).rejects.toBeInstanceOf(RateLimitError);
  });

  it('does not attach an internal timeout signal when none is supplied', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        new Response(sseBody(), { status: 200, headers: { 'content-type': 'text/event-stream' } }),
      );
    const c = new HttpClient({
      apiKey: 'sk_test',
      fetch: fetchMock as unknown as typeof fetch,
      timeout: 5,
    });
    await c.stream({ path: '/x' });
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(init.signal).toBeUndefined();
  });
});
