import { http, HttpResponse } from 'msw';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import { BimpeAI, RateLimitError } from '../../src';
import { API_BASE, createMswServer } from '../helpers/msw-server';

const TICKET_PATH = `${API_BASE}/agents/:agentId/conversations/:conversationId/stream-ticket`;
const STREAM_PATH = `${API_BASE}/agents/:agentId/conversations/:conversationId/messages/stream`;

const encoder = new TextEncoder();

const messageFrame = (id: string, role = 'user') =>
  `id: ${id}\nevent: message\ndata: ${JSON.stringify({
    id,
    conversation_id: 'cv_1',
    role,
    message: 'hi',
    message_type: 'text',
    created_at: 'now',
  })}\n\n`;

const heartbeatFrame = (ts: number) => `event: heartbeat\ndata: {"ts":${ts}}\n\n`;

const ticketHandler = http.post(TICKET_PATH, () =>
  HttpResponse.json({ message: 'ok', data: { ticket: 't1', expires_in: 60 } }, { status: 201 }),
);

const server = createMswServer([ticketHandler]);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

const client = () => new BimpeAI({ apiKey: 'sk_test', baseUrl: 'https://api.bimpeai.test' });

describe('message streaming integration', () => {
  it('yields message events over a real event-stream and skips heartbeats', async () => {
    server.use(
      ticketHandler,
      http.get(STREAM_PATH, () => {
        const body = new ReadableStream<Uint8Array>({
          start(controller) {
            controller.enqueue(encoder.encode(messageFrame('m_1')));
            controller.enqueue(encoder.encode(heartbeatFrame(1)));
            controller.enqueue(encoder.encode(messageFrame('m_2', 'assistant')));
            controller.close();
          },
        });
        return new HttpResponse(body, { headers: { 'content-type': 'text/event-stream' } });
      }),
    );

    const ids: string[] = [];
    for await (const event of client().conversations.messages.stream('a_1', 'cv_1', {
      reconnect: false,
    })) {
      ids.push(event.id);
    }
    expect(ids).toEqual(['m_1', 'm_2']);
  });

  it('throws RateLimitError when the stream open is rate limited', async () => {
    server.use(
      ticketHandler,
      http.get(STREAM_PATH, () =>
        HttpResponse.json({ message: 'too many', code: 'too_many_requests' }, { status: 429 }),
      ),
    );

    const iterate = async () => {
      for await (const _event of client().conversations.messages.stream('a_1', 'cv_1', {
        reconnect: false,
      })) {
        // drain
      }
    };
    await expect(iterate()).rejects.toBeInstanceOf(RateLimitError);
  });
});
