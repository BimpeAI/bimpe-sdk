import type { HttpClient } from '../../core/http-client';
import type { Call } from './types';

export class Calls {
  constructor(private readonly client: Pick<HttpClient, 'request'>) {}

  async list(): Promise<readonly Call[]> {
    const res = await this.client.request<Call[]>({ method: 'GET', path: '/calls' });
    return res.data;
  }
}
