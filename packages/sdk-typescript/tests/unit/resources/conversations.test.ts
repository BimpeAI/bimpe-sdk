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
  it('list() GETs the nested path with filters', async () => {
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
      is_test_channel: false,
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
        is_test_channel: false,
        is_ai_chat_paused: undefined,
        needs_attention: true,
      },
    });
  });

  it('retrieve() GETs a single conversation', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ id: 'cv_1' }));
    const c = await make(requestImpl).retrieve('a_1', 'cv_1');
    expect(c.id).toBe('cv_1');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/agents/a_1/conversations/cv_1',
    });
  });

  it('createOrSendMessage() Mode A POSTs unified path with conversation_id', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        id: 'm_1',
        role: 'user',
        message: 'Hi',
        message_type: 'text',
        created_at: 'now',
        conversation_id: 'cv_1',
      }),
    );
    const out = await make(requestImpl).createOrSendMessage(
      'a_1',
      { conversation_id: 'cv_1', message: 'Hi' },
      { idempotencyKey: 'op-1' },
    );
    expect(out.conversation_id).toBe('cv_1');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/conversations/messages',
      body: { conversation_id: 'cv_1', message: 'Hi' },
      idempotencyKey: 'op-1',
    });
  });

  it('createOrSendMessage() Mode B POSTs channel_type + channel_user_id', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        id: 'm_1',
        role: 'user',
        message: 'Hi',
        message_type: 'text',
        created_at: 'now',
        conversation_id: 'cv_new',
      }),
    );
    await make(requestImpl).createOrSendMessage('a_1', {
      message: 'Hi',
      channel_type: 'whatsapp',
      channel_user_id: '+2348012345678',
    });
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/conversations/messages',
      body: {
        message: 'Hi',
        channel_type: 'whatsapp',
        channel_user_id: '+2348012345678',
      },
    });
  });

  it('updateAiStatus() PATCHes ai-status', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse({ is_ai_chat_paused: true }));
    const out = await make(requestImpl).updateAiStatus('a_1', 'cv_1', {
      is_ai_chat_paused: true,
    });
    expect(out.is_ai_chat_paused).toBe(true);
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
