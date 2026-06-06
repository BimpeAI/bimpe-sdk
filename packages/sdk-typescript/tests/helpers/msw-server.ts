import type { RequestHandler } from 'msw';
import { setupServer } from 'msw/node';

export const API_BASE = 'https://api.bimpeai.test/api/v1/console';

export function createMswServer(handlers: RequestHandler[]) {
  return setupServer(...handlers);
}
