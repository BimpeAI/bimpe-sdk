import type { RequestExecutor } from '../../core/types';
import type { Call } from './types';

export class Calls {
  constructor(private readonly client: RequestExecutor) {}

  async list(): Promise<readonly Call[]> {
    const res = await this.client.request<Call[]>({ method: 'GET', path: '/calls' });
    return res.data;
  }
}
