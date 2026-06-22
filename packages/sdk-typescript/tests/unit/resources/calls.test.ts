import { describe, expect, it, vi } from 'vitest';
import { Page } from '../../../src/core/pagination';
import { Calls } from '../../../src/resources/calls/calls';

const okResponse = <T>(data: T, meta: unknown = null) => ({
  data,
  meta,
  requestId: 'r1',
  status: 200,
  headers: new Headers(),
});

const make = (requestImpl: ReturnType<typeof vi.fn>) =>
  new Calls({ request: requestImpl } as never);

describe('Calls resource', () => {
  it('list() GETs the agent-scoped path and returns a Page', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse(
        [
          {
            id: 'call_1',
            source: null,
            destination: '+15551234567',
            status: 'ended',
            direction: 'outbound',
            created_on: 'now',
            duration_seconds: 42,
            is_test_call: false,
            error_reason: null,
            end_reason: 'completed',
            ringing_at: null,
            ended_at: 'now',
          },
        ],
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
    const page = await make(requestImpl).list('a_1', { status: 'ended', is_test_call: false });
    expect(page).toBeInstanceOf(Page);
    expect(page.data[0]?.id).toBe('call_1');
    expect(page.data[0]?.status).toBe('ended');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/agents/a_1/calls',
      query: {
        page: 1,
        limit: undefined,
        search: undefined,
        sort: undefined,
        is_test_call: false,
        status: 'ended',
      },
    });
  });

  it('make() POSTs the agent-scoped path and returns a MakeCallResult', async () => {
    const requestImpl = vi
      .fn()
      .mockResolvedValue(okResponse({ status: 'initiated', call_id: 'call_1', detail: 'dialing' }));
    const result = await make(requestImpl).make(
      'a_1',
      { destination: '+15551234567', is_test_call: false },
      { idempotencyKey: 'op-1' },
    );
    expect(result.status).toBe('initiated');
    expect(result.call_id).toBe('call_1');
    expect(result.detail).toBe('dialing');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/calls',
      body: { destination: '+15551234567', is_test_call: false },
      idempotencyKey: 'op-1',
    });
  });

  it('retrieve() GETs a single call and returns the detail shape', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        id: 'call_1',
        source: null,
        destination: '+15551234567',
        status: 'ended',
        direction: 'outbound',
        created_on: 'now',
        duration_seconds: 42,
        is_test_call: false,
        error_reason: null,
        end_reason: 'completed',
        ringing_at: null,
        ended_at: 'now',
        started_at: 'now',
        answered_at: 'now',
        conversation_logs: [
          {
            id: 'log_1',
            role: 'assistant',
            message: 'Hello',
            message_type: 'text',
            created_at: 'now',
          },
        ],
      }),
    );
    const detail = await make(requestImpl).retrieve('a_1', 'call_1');
    expect(detail.id).toBe('call_1');
    expect(detail.conversation_logs[0]?.id).toBe('log_1');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/agents/a_1/calls/call_1',
    });
  });
});
