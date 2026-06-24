import { describe, expect, it, vi } from 'vitest';
import { Page } from '../../../src/core/pagination';
import { PhoneNumbers } from '../../../src/resources/phone-numbers/phone-numbers';

const okResponse = <T>(data: T, meta: unknown = null) => ({
  data,
  meta,
  requestId: 'r1',
  status: 200,
  headers: new Headers(),
});

const make = (requestImpl: ReturnType<typeof vi.fn>) =>
  new PhoneNumbers({ request: requestImpl } as never);

const META = {
  total_count: 1,
  page_count: 1,
  current_page: 1,
  limit: 20,
  has_next_page: false,
  has_previous_page: false,
};

describe('PhoneNumbers resource', () => {
  it('list() GETs /phone-numbers and returns a Page', async () => {
    const requestImpl = vi
      .fn()
      .mockResolvedValue(
        okResponse([{ id: 'pn_1', agent_id: null, label: null, e164: '+15551234567' }], META),
      );
    const page = await make(requestImpl).list({ search: 'support' });
    expect(page).toBeInstanceOf(Page);
    expect(page.data[0]?.id).toBe('pn_1');
    expect(page.data[0]?.e164).toBe('+15551234567');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/phone-numbers',
      query: { page: 1, limit: undefined, search: 'support', sort: undefined },
    });
  });

  it('retrieve() GETs a single number and returns the detail shape', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        id: 'pn_1',
        agent_id: 'a_1',
        label: 'Support line',
        e164: '+15551234567',
        created_at: 'now',
        updated_at: 'now',
        inbound_enabled: true,
      }),
    );
    const detail = await make(requestImpl).retrieve('pn_1');
    expect(detail.inbound_enabled).toBe(true);
    expect(detail.agent_id).toBe('a_1');
    expect(requestImpl).toHaveBeenCalledWith({ method: 'GET', path: '/phone-numbers/pn_1' });
  });

  it('update() PATCHes the number to link an agent and set a label', async () => {
    const requestImpl = vi.fn().mockResolvedValue(
      okResponse({
        id: 'pn_1',
        agent_id: 'a_2',
        label: 'Sales',
        e164: '+15551234567',
        created_at: 'now',
        updated_at: 'now',
        inbound_enabled: true,
      }),
    );
    const detail = await make(requestImpl).update(
      'pn_1',
      { agent_id: 'a_2', label: 'Sales' },
      { idempotencyKey: 'op-1' },
    );
    expect(detail.agent_id).toBe('a_2');
    expect(detail.label).toBe('Sales');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'PATCH',
      path: '/phone-numbers/pn_1',
      body: { agent_id: 'a_2', label: 'Sales' },
      idempotencyKey: 'op-1',
    });
  });

  it('requests.list() GETs /phone-numbers/request and returns a Page', async () => {
    const requestImpl = vi
      .fn()
      .mockResolvedValue(
        okResponse([{ id: 'pn_2', agent_id: null, label: null, e164: '+15559999999' }], META),
      );
    const page = await make(requestImpl).requests.list();
    expect(page).toBeInstanceOf(Page);
    expect(page.data[0]?.id).toBe('pn_2');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/phone-numbers/request',
      query: { page: 1, limit: undefined, search: undefined, sort: undefined },
    });
  });

  it('requests.create() POSTs /phone-numbers/request and resolves to void', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse(null));
    const result = await make(requestImpl).requests.create(
      {
        business_name: 'Acme Support Ltd',
        intended_use: 'Inbound support',
        region: 'ng',
        agent_count: 1,
        outbound_minutes: 500,
      },
      { idempotencyKey: 'op-2' },
    );
    expect(result).toBeUndefined();
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/phone-numbers/request',
      body: {
        business_name: 'Acme Support Ltd',
        intended_use: 'Inbound support',
        region: 'ng',
        agent_count: 1,
        outbound_minutes: 500,
      },
      idempotencyKey: 'op-2',
    });
  });

  it('exposes the nested requests resource', () => {
    expect(make(vi.fn()).requests).toBeDefined();
  });
});
