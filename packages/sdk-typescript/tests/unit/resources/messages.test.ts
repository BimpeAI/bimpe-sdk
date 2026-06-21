import { describe, expect, it, vi } from 'vitest';
import { Page } from '../../../src/core/pagination';
import { Messages } from '../../../src/resources/conversations/messages';

const okResponse = <T>(data: T, meta: unknown = null) => ({
  data,
  meta,
  requestId: 'r1',
  status: 200,
  headers: new Headers(),
});

const make = (requestImpl: ReturnType<typeof vi.fn>) =>
  new Messages({ request: requestImpl } as never);

describe('Messages resource', () => {
  it('list() GETs the nested messages path', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse(
        [{ id: 'm_1', role: 'user', message: 'hi', message_type: 'text', created_at: 'now' }],
        {
          total_count: 1,
          page_count: 1,
          current_page: 1,
          limit: 20,
          has_next_page: false,
          has_previous_page: false,
        },
      ),
    );
    const page = await make(requestImpl).list('a_1', 'cv_1', {
      search: 'refund',
      sort: '-created_at',
    });
    expect(page).toBeInstanceOf(Page);
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/agents/a_1/conversations/cv_1/messages',
      query: { page: 1, limit: undefined, search: 'refund', sort: '-created_at' },
    });
  });

  it('send() POSTs a message with a role and an idempotencyKey', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        id: 'm_2',
        role: 'assistant',
        message: 'hello',
        message_type: 'text',
        created_at: 'now',
      }),
    );
    const m = await make(requestImpl).send(
      'a_1',
      'cv_1',
      { message: 'Hi', role: 'assistant' },
      { idempotencyKey: 'op-1' },
    );
    expect(m.id).toBe('m_2');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/conversations/cv_1/messages',
      body: { message: 'Hi', role: 'assistant' },
      idempotencyKey: 'op-1',
    });
  });

  it('retrieve() GETs a single message and returns it with attachments', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        id: 'm_3',
        role: 'user',
        message: 'see attachment',
        message_type: 'text',
        created_at: 'now',
        attachments: [{ type: 'image', url: 'https://x' }],
      }),
    );
    const m = await make(requestImpl).retrieve('a_1', 'cv_1', 'm_3');
    expect(m.id).toBe('m_3');
    expect(m.attachments?.[0]?.url).toBe('https://x');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/agents/a_1/conversations/cv_1/messages/m_3',
    });
  });
});
