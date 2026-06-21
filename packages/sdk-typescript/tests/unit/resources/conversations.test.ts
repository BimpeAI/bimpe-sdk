import { describe, expect, it, vi } from 'vitest';
import { Page } from '../../../src/core/pagination';
import { Conversations } from '../../../src/resources/conversations/conversations';

const okResponse = <T>(data: T, meta: unknown = null) => ({
  data,
  meta,
  requestId: 'r1',
  status: 200,
  headers: new Headers(),
});

const make = (requestImpl: ReturnType<typeof vi.fn>) =>
  new Conversations({ request: requestImpl } as never);

describe('Conversations resource', () => {
  it('list() GETs the nested path and forwards every filter', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse([{ id: 'cv_1' }], {
        total_count: 1,
        page_count: 1,
        current_page: 1,
        limit: 20,
        has_next_page: false,
        has_previous_page: false,
      }),
    );
    const page = await make(requestImpl).list('a_1', {
      channel: 'whatsapp',
      sort: '-created_at',
      is_test_channel: false,
      is_ai_chat_paused: true,
      needs_attention: true,
    });
    expect(page).toBeInstanceOf(Page);
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/agents/a_1/conversations',
      query: {
        page: 1,
        limit: undefined,
        search: undefined,
        channel: 'whatsapp',
        sort: '-created_at',
        is_test_channel: false,
        is_ai_chat_paused: true,
        needs_attention: true,
      },
    });
  });

  it('retrieve() GETs a single conversation and returns the detail shape', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        id: 'cv_1',
        channel_type: 'whatsapp',
        full_name: 'Ada Lovelace',
        email: 'ada@example.com',
        phone_number: '+15551234567',
        profile_picture: null,
      }),
    );
    const c = await make(requestImpl).retrieve('a_1', 'cv_1');
    expect(c.id).toBe('cv_1');
    expect(c.full_name).toBe('Ada Lovelace');
    expect(c.email).toBe('ada@example.com');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/agents/a_1/conversations/cv_1',
    });
  });

  it('send() POSTs the collection-level messages path and returns a Message', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        id: 'm_1',
        role: 'user',
        message: 'Hi there',
        message_type: 'text',
        created_at: 'now',
      }),
    );
    const body = {
      message: 'Hi there',
      channel_type: 'whatsapp' as const,
      channel_user_id: '+15551234567',
      channel_username: 'ada',
    };
    const m = await make(requestImpl).send('a_1', body, { idempotencyKey: 'op-1' });
    expect(m.id).toBe('m_1');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/conversations/messages',
      body,
      idempotencyKey: 'op-1',
    });
  });

  it('setAiStatus() PATCHes the ai-status path and returns the status', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ is_ai_chat_paused: true }));
    const status = await make(requestImpl).setAiStatus('a_1', 'cv_1', {
      is_ai_chat_paused: true,
    });
    expect(status.is_ai_chat_paused).toBe(true);
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'PATCH',
      path: '/agents/a_1/conversations/cv_1/ai-status',
      body: { is_ai_chat_paused: true },
    });
  });

  it('exposes the nested messages resource', () => {
    expect(make(vi.fn()).messages).toBeDefined();
  });
});
