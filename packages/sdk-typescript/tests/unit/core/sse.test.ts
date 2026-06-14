import { describe, expect, it } from 'vitest';
import { type SseEvent, parseSse } from '../../../src/core/sse';

function streamFrom(chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  let i = 0;
  return new ReadableStream<Uint8Array>({
    pull(controller) {
      if (i < chunks.length) controller.enqueue(encoder.encode(chunks[i++]));
      else controller.close();
    },
  });
}

async function collect(chunks: string[]): Promise<SseEvent[]> {
  const events: SseEvent[] = [];
  for await (const event of parseSse(streamFrom(chunks))) events.push(event);
  return events;
}

describe('parseSse', () => {
  it('parses a single event with id, event, and data', async () => {
    const events = await collect(['id: m_1\nevent: message\ndata: {"a":1}\n\n']);
    expect(events).toEqual([{ id: 'm_1', event: 'message', data: '{"a":1}' }]);
  });

  it('joins multiple data lines with newlines', async () => {
    const events = await collect(['data: line1\ndata: line2\n\n']);
    expect(events[0]?.data).toBe('line1\nline2');
  });

  it('ignores comment lines and keep-alive colons', async () => {
    const events = await collect([': keep-alive\n\n', 'data: real\n\n']);
    expect(events).toEqual([{ data: 'real' }]);
  });

  it('does not emit a frame that has no data', async () => {
    const events = await collect(['event: ping\n\n', 'data: x\n\n']);
    expect(events).toEqual([{ data: 'x' }]);
  });

  it('handles CRLF line endings', async () => {
    const events = await collect(['event: message\r\ndata: hi\r\n\r\n']);
    expect(events).toEqual([{ event: 'message', data: 'hi' }]);
  });

  it('parses an event split across chunk boundaries', async () => {
    const events = await collect(['id: m_2\nev', 'ent: message\nda', 'ta: split\n', '\n']);
    expect(events).toEqual([{ id: 'm_2', event: 'message', data: 'split' }]);
  });

  it('reassembles a CRLF terminator split across chunks', async () => {
    const events = await collect(['data: x\r', '\n\r\n']);
    expect(events).toEqual([{ data: 'x' }]);
  });

  it('yields multiple events from one stream', async () => {
    const events = await collect([
      'id: 1\nevent: message\ndata: {"id":"1"}\n\nid: 2\nevent: heartbeat\ndata: {"ts":9}\n\n',
    ]);
    expect(events).toEqual([
      { id: '1', event: 'message', data: '{"id":"1"}' },
      { id: '2', event: 'heartbeat', data: '{"ts":9}' },
    ]);
  });
});
