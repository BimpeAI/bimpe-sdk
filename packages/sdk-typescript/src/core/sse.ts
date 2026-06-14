export interface SseEvent {
  readonly id?: string;
  readonly event?: string;
  readonly data: string;
}

interface Accumulator {
  id?: string;
  event?: string;
  data: string[];
}

/**
 * Parse a byte stream of Server-Sent Events into frames, following the W3C event
 * stream format: `field: value` lines, `data` lines joined with newlines, a blank
 * line dispatching the accumulated event, and `:` comment lines ignored. Frames
 * with no data are not emitted (e.g. lone comments or keep-alive colons).
 *
 * Line terminators `\n` and `\r\n` are handled, including a `\r\n` split across
 * chunk boundaries. Lone `\r` terminators are not used by SSE servers and are not
 * treated as line breaks.
 */
export async function* parseSse(stream: ReadableStream<Uint8Array>): AsyncGenerator<SseEvent> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let frame: Accumulator = { data: [] };

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let newline: number;
      // biome-ignore lint/suspicious/noAssignInExpressions: idiomatic incremental line scan
      while ((newline = buffer.indexOf('\n')) !== -1) {
        let line = buffer.slice(0, newline);
        buffer = buffer.slice(newline + 1);
        if (line.endsWith('\r')) line = line.slice(0, -1);

        if (line === '') {
          const event = flush(frame);
          if (event) yield event;
          frame = { data: [] };
          continue;
        }
        if (line.startsWith(':')) continue;

        const colon = line.indexOf(':');
        const field = colon === -1 ? line : line.slice(0, colon);
        let value = colon === -1 ? '' : line.slice(colon + 1);
        if (value.startsWith(' ')) value = value.slice(1);

        if (field === 'event') frame.event = value;
        else if (field === 'data') frame.data.push(value);
        else if (field === 'id') frame.id = value;
      }
    }
  } finally {
    reader.releaseLock();
  }
}

function flush(frame: Accumulator): SseEvent | null {
  if (frame.data.length === 0) return null;
  const event: { id?: string; event?: string; data: string } = { data: frame.data.join('\n') };
  if (frame.id !== undefined) event.id = frame.id;
  if (frame.event !== undefined) event.event = frame.event;
  return event;
}
