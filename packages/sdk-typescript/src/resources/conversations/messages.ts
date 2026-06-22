import { Page, PagePromise } from '../../core/pagination';
import { computeBackoff, shouldRetry } from '../../core/retries';
import { parseSse } from '../../core/sse';
import type { RequestOptions, Transport } from '../../core/types';
import type {
  ListMessagesQuery,
  Message,
  SendMessageBody,
  StreamMessageEvent,
  StreamOptions,
  StreamTicket,
} from './types';

const DEFAULT_STREAM_RETRIES = 5;

export class Messages {
  constructor(private readonly client: Transport) {}

  list(
    agentId: string,
    conversationId: string,
    query: ListMessagesQuery = {},
  ): PagePromise<Message> {
    return new PagePromise(() => this.fetchPage(agentId, conversationId, query.page ?? 1, query));
  }

  async send(
    agentId: string,
    conversationId: string,
    body: SendMessageBody,
    options: RequestOptions = {},
  ): Promise<Message> {
    const res = await this.client.request<Message>({
      method: 'POST',
      path: `/agents/${agentId}/conversations/${conversationId}/messages`,
      body,
      ...options,
    });
    return res.data;
  }

  async retrieve(agentId: string, conversationId: string, messageId: string): Promise<Message> {
    const res = await this.client.request<Message>({
      method: 'GET',
      path: `/agents/${agentId}/conversations/${conversationId}/messages/${messageId}`,
    });
    return res.data;
  }

  /** Issue a single-use, short-lived ticket for opening the message stream. */
  async streamTicket(
    agentId: string,
    conversationId: string,
    options: RequestOptions = {},
  ): Promise<StreamTicket> {
    const res = await this.client.request<StreamTicket>({
      method: 'POST',
      path: `/agents/${agentId}/conversations/${conversationId}/stream-ticket`,
      ...options,
    });
    return res.data;
  }

  /**
   * Open a live stream of conversation messages over Server-Sent Events. Issues a
   * ticket, opens the stream, and yields each `message` event; heartbeats are
   * consumed internally. On a dropped connection it re-issues a ticket and resumes
   * from the last seen id (disable with `reconnect: false`).
   */
  stream(
    agentId: string,
    conversationId: string,
    options: StreamOptions = {},
  ): AsyncIterable<StreamMessageEvent> {
    const client = this.client;
    const issueTicket = (signal?: AbortSignal) =>
      this.streamTicket(agentId, conversationId, signal ? { signal } : {});
    const streamPath = `/agents/${agentId}/conversations/${conversationId}/messages/stream`;
    const reconnect = options.reconnect !== false;
    const maxRetries = options.maxRetries ?? DEFAULT_STREAM_RETRIES;

    return {
      async *[Symbol.asyncIterator](): AsyncIterator<StreamMessageEvent> {
        let after = options.after;
        let attempt = 0;

        while (true) {
          let response: Response;
          try {
            const { ticket } = await issueTicket(options.signal);
            response = await client.stream({
              path: streamPath,
              query: { ticket, ...(after ? { after } : {}) },
              ...(options.signal ? { signal: options.signal } : {}),
            });
          } catch (error) {
            if (isAborted(options.signal)) return;
            if (reconnect && shouldRetry(error, attempt, maxRetries)) {
              await sleep(computeBackoff(attempt));
              attempt += 1;
              continue;
            }
            throw error;
          }

          if (!response.body) return;

          try {
            for await (const frame of parseSse(response.body)) {
              if (frame.event !== 'message') continue;
              const event = parseMessage(frame.data);
              if (!event) continue;
              if (frame.id) after = frame.id;
              attempt = 0;
              yield event;
            }
          } catch (error) {
            if (isAborted(options.signal)) return;
            if (reconnect && shouldRetry(error, attempt, maxRetries)) {
              await sleep(computeBackoff(attempt));
              attempt += 1;
              continue;
            }
            throw error;
          }

          // The server closed the stream. Reconnect from the last id, or stop.
          if (!reconnect || isAborted(options.signal) || attempt >= maxRetries) return;
          await sleep(computeBackoff(attempt));
          attempt += 1;
        }
      },
    };
  }

  private async fetchPage(
    agentId: string,
    conversationId: string,
    page: number,
    query: ListMessagesQuery,
  ): Promise<Page<Message>> {
    const res = await this.client.request<Message[]>({
      method: 'GET',
      path: `/agents/${agentId}/conversations/${conversationId}/messages`,
      query: { page, limit: query.limit, search: query.search, sort: query.sort },
    });
    return new Page<Message>({
      data: res.data,
      meta: res.meta,
      requestId: res.requestId,
      fetcher: (next) => this.fetchPage(agentId, conversationId, next, query),
    });
  }
}

function parseMessage(data: string): StreamMessageEvent | null {
  try {
    return JSON.parse(data) as StreamMessageEvent;
  } catch {
    return null;
  }
}

function isAborted(signal?: AbortSignal): boolean {
  return signal?.aborted === true;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
