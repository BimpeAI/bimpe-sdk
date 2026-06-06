import { HttpClient, type HttpClientConfig } from './core/http-client';
import type { ApiResponse, InternalRequestSpec, RequestOptions } from './core/types';

export type BimpeAIConfig = HttpClientConfig;

export class BimpeAI {
  private readonly http: HttpClient;

  constructor(config: BimpeAIConfig) {
    this.http = new HttpClient(config);
  }

  request<T>(spec: InternalRequestSpec & RequestOptions): Promise<ApiResponse<T>> {
    return this.http.request<T>(spec);
  }
}
