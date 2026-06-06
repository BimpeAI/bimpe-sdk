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
  it('list() GETs the nested path with a channel filter', async () => {
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
    const page = await make(requestImpl).list('a_1', { channel: 'whatsapp' });
    expect(page).toBeInstanceOf(Page);
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/agents/a_1/conversations',
      query: { page: 1, limit: undefined, search: undefined, channel: 'whatsapp' },
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

  it('exposes the nested messages resource', () => {
    expect(make(vi.fn()).messages).toBeDefined();
  });
});
