import { HttpClient, type HttpClientConfig } from './core/http-client';
import type { ApiResponse, InternalRequestSpec, RequestOptions } from './core/types';
import { Agents } from './resources/agents';

export type BimpeAIConfig = HttpClientConfig;

export class BimpeAI {
  readonly agents: Agents;
  private readonly http: HttpClient;

  constructor(config: BimpeAIConfig) {
    this.http = new HttpClient(config);
    this.agents = new Agents(this.http);
  }

  request<T>(spec: InternalRequestSpec & RequestOptions): Promise<ApiResponse<T>> {
    return this.http.request<T>(spec);
  }
}
