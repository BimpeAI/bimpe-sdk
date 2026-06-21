import type { RequestExecutor, RequestOptions } from '../../core/types';
import type { Call, MakeCallBody, QueueCallBody } from './types';

export class Calls {
  constructor(private readonly client: RequestExecutor) {}

  async list(): Promise<readonly Call[]> {
    const res = await this.client.request<Call[]>({ method: 'GET', path: '/calls' });
    return res.data;
  }

  async make(body: MakeCallBody, options: RequestOptions = {}): Promise<unknown> {
    const res = await this.client.request<unknown>({
      method: 'POST',
      path: '/calls',
      body,
      ...options,
    });
    return res.data;
  }

  async queue(body: QueueCallBody, options: RequestOptions = {}): Promise<unknown> {
    const res = await this.client.request<unknown>({
      method: 'POST',
      path: '/calls/queue',
      body,
      ...options,
    });
    return res.data;
  }
}
