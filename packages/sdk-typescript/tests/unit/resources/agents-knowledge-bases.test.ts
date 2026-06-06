import { describe, expect, it, vi } from 'vitest';
import { AgentKnowledgeBases } from '../../../src/resources/agents/knowledge-bases';

const okResponse = <T>(data: T) => ({
  data,
  meta: null,
  requestId: 'r1',
  status: 200,
  headers: new Headers(),
});

const make = (requestImpl: ReturnType<typeof vi.fn>) =>
  new AgentKnowledgeBases({ request: requestImpl } as never);

describe('AgentKnowledgeBases resource', () => {
  it('list() GETs /agents/{id}/knowledge_bases', async () => {
    const requestImpl = vi
      .fn()
      .mockResolvedValue(okResponse([{ id: 'k_1', type: 'text', name: 'FAQ', description: null }]));
    const out = await make(requestImpl).list('a_1');
    expect(out[0]?.id).toBe('k_1');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'GET',
      path: '/agents/a_1/knowledge_bases',
    });
  });

  it('create() POSTs a text knowledge base with idempotencyKey', async () => {
    const requestImpl = vi
      .fn()
      .mockResolvedValue(okResponse({ id: 'k_1', type: 'text', name: 'FAQ', description: null }));
    const kb = await make(requestImpl).create(
      'a_1',
      { type: 'text', name: 'FAQ', content: 'hello' },
      { idempotencyKey: 'op-1' },
    );
    expect(kb.type).toBe('text');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'POST',
      path: '/agents/a_1/knowledge_bases',
      body: { type: 'text', name: 'FAQ', content: 'hello' },
      idempotencyKey: 'op-1',
    });
  });

  it('update() PATCHes /agents/{id}/knowledge_bases/{kbId}', async () => {
    const requestImpl = vi
      .fn()
      .mockResolvedValue(okResponse({ id: 'k_1', type: 'text', name: 'New', description: null }));
    const kb = await make(requestImpl).update('a_1', 'k_1', { name: 'New' });
    expect(kb.name).toBe('New');
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'PATCH',
      path: '/agents/a_1/knowledge_bases/k_1',
      body: { name: 'New' },
    });
  });

  it('delete() DELETEs /agents/{id}/knowledge_bases/{kbId} and returns void', async () => {
    const requestImpl = vi.fn().mockResolvedValue(okResponse(null));
    await expect(make(requestImpl).delete('a_1', 'k_1')).resolves.toBeUndefined();
    expect(requestImpl).toHaveBeenCalledWith({
      method: 'DELETE',
      path: '/agents/a_1/knowledge_bases/k_1',
    });
  });
});
