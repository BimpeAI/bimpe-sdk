import { HttpClient, type HttpClientConfig } from './core/http-client';
import type {
  ApiResponse,
  InternalRequestSpec,
  RequestExecutor,
  RequestOptions,
} from './core/types';
import { Agents } from './resources/agents';
import { Calls } from './resources/calls';
import { Conversations } from './resources/conversations';
import { Workflows } from './resources/workflows';

export type BimpeAIConfig = HttpClientConfig;

export class BimpeAI {
  readonly agents: Agents;
  readonly workflows: Workflows;
  readonly conversations: Conversations;
  readonly calls: Calls;
  private readonly http: RequestExecutor;

  constructor(config: BimpeAIConfig) {
    this.http = new HttpClient(config);
    this.agents = new Agents(this.http);
    this.workflows = new Workflows(this.http);
    this.conversations = new Conversations(this.http);
    this.calls = new Calls(this.http);
  }

  request<T>(spec: InternalRequestSpec & RequestOptions): Promise<ApiResponse<T>> {
    return this.http.request<T>(spec);
  }
}
