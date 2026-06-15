import { describe, expect, it, vi } from 'vitest';
import { Messages } from '../../../src/resources/conversations/messages';
import type { StreamMessageEvent } from '../../../src/resources/conversations/types';

const ticketResponse = (ticket: string) => ({
  data: { ticket, expires_in: 60 },
  meta: null,
  requestId: 'r',
  status: 201,
  headers: new Headers(),
});

const msg = (id: string, role = 'user') =>
  `id: ${id}\nevent: message\ndata: ${JSON.stringify({
    id,
    conversation_id: 'cv_1',
    role,
    message: 'hi',
    message_type: 'text',
    created_at: 'now',
  })}\n\n`;

const heartbeat = (ts: number) => `event: heartbeat\ndata: {"ts":${ts}}\n\n`;

function sseResponse(frames: string): Response {
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(new TextEncoder().encode(frames));
      controller.close();
    },
  });
  return new Response(body, { status: 200, headers: { 'content-type': 'text/event-stream' } });
}

const makeTransport = (stream: ReturnType<typeof vi.fn>, request?: ReturnType<typeof vi.fn>) => ({
  request: request ?? vi.fn().mockResolvedValue(ticketResponse('t1')),
  stream,
});

describe('Messages.streamTicket', () => {
  it('POSTs the stream-ticket endpoint and returns the ticket', async () => {
    const request = vi.fn().mockResolvedValue(ticketResponse('tk_1'));
    const messages = new Messages(makeTransport(vi.fn(), request) as never);
    const ticket = await messages.streamTicket('a_1', 'cv_1');
    expect(ticket).toEqual({ ticket: 'tk_1', expires_in: 60 });
    expect(request).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/conversations/cv_1/stream-ticket',
    });
  });
});

describe('Messages.stream', () => {
  it('yields message events, skips heartbeats, and opens with a ticket', async () => {
    const stream = vi
      .fn()
      .mockResolvedValue(sseResponse(msg('m_1') + heartbeat(1) + msg('m_2', 'assistant')));
    const messages = new Messages(makeTransport(stream) as never);

    const ids: string[] = [];
    for await (const event of messages.stream('a_1', 'cv_1', { reconnect: false })) {
      ids.push((event as StreamMessageEvent).id);
    }
    expect(ids).toEqual(['m_1', 'm_2']);
    expect(stream).toHaveBeenCalledWith(
      expect.objectContaining({
        path: '/agents/a_1/conversations/cv_1/messages/stream',
        query: { ticket: 't1' },
      }),
    );
  });

  it('reconnects after the stream ends, resuming from the last id', async () => {
    const stream = vi
      .fn()
      .mockResolvedValueOnce(sseResponse(msg('m_1')))
      .mockResolvedValueOnce(sseResponse(msg('m_2')));
    const messages = new Messages(makeTransport(stream) as never);

    const ids: string[] = [];
    for await (const event of messages.stream('a_1', 'cv_1')) {
      ids.push(event.id);
      if (ids.length === 2) break;
    }
    expect(ids).toEqual(['m_1', 'm_2']);
    expect(stream.mock.calls[1]?.[0]).toMatchObject({ query: { ticket: 't1', after: 'm_1' } });
  });

  it('stops quietly when the caller has aborted', async () => {
    const controller = new AbortController();
    controller.abort();
    const request = vi.fn().mockRejectedValue(new Error('aborted'));
    const messages = new Messages(makeTransport(vi.fn(), request) as never);

    const ids: string[] = [];
    for await (const event of messages.stream('a_1', 'cv_1', { signal: controller.signal })) {
      ids.push(event.id);
    }
    expect(ids).toEqual([]);
  });

  it('stops cleanly when the caller aborts mid-stream', async () => {
    const controller = new AbortController();
    // A body that delivers one message, then rejects the next read once aborted —
    // mirroring how fetch tears down a streamed response body on abort.
    const body = new ReadableStream<Uint8Array>({
      start(c) {
        c.enqueue(new TextEncoder().encode(msg('m_1')));
      },
      pull() {
        return new Promise<void>((_, reject) => {
          controller.signal.addEventListener(
            'abort',
            () => reject(new DOMException('aborted', 'AbortError')),
            { once: true },
          );
        });
      },
    });
    const response = new Response(body, {
      status: 200,
      headers: { 'content-type': 'text/event-stream' },
    });
    const messages = new Messages(makeTransport(vi.fn().mockResolvedValue(response)) as never);

    const ids: string[] = [];
    for await (const event of messages.stream('a_1', 'cv_1', { signal: controller.signal })) {
      ids.push(event.id);
      controller.abort();
    }
    expect(ids).toEqual(['m_1']);
  });
});
