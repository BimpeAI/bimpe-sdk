import type { RequestExecutor, RequestOptions } from '../../core/types';
import type {
  AgentIntegration,
  BimpeaiConfigureBody,
  BimpeaiIntegration,
  CustomApiConfigureBody,
  CustomApiCreateToolBody,
  CustomApiIntegration,
  IntegrationTool,
  McpServerConfigureBody,
  McpServerDiscoverResult,
  McpServerIntegration,
  McpServerTestResult,
  OnboardingUrl,
  PipedreamConfigureBody,
  PipedreamIntegration,
} from './types';

export class AgentBimpeaiIntegrations {
  constructor(private readonly client: RequestExecutor) {}

  async list(agentId: string): Promise<readonly BimpeaiIntegration[]> {
    const res = await this.client.request<BimpeaiIntegration[]>({
      method: 'GET',
      path: `/agents/${agentId}/integrations/bimpeai`,
    });
    return res.data;
  }

  async configure(
    agentId: string,
    body: BimpeaiConfigureBody,
    options: RequestOptions = {},
  ): Promise<OnboardingUrl> {
    const res = await this.client.request<OnboardingUrl>({
      method: 'POST',
      path: `/agents/${agentId}/integrations/bimpeai/configure`,
      body,
      ...options,
    });
    return res.data;
  }

  async disconnect(agentId: string, integrationId: string): Promise<void> {
    await this.client.request<unknown>({
      method: 'DELETE',
      path: `/agents/${agentId}/integrations/bimpeai/${integrationId}`,
    });
  }
}

export class AgentCustomApiTools {
  constructor(private readonly client: RequestExecutor) {}

  async list(agentId: string, integrationId: string): Promise<readonly IntegrationTool[]> {
    const res = await this.client.request<IntegrationTool[]>({
      method: 'GET',
      path: `/agents/${agentId}/integrations/custom_api/${integrationId}/tools`,
    });
    return res.data;
  }

  async add(
    agentId: string,
    integrationId: string,
    body: CustomApiCreateToolBody,
    options: RequestOptions = {},
  ): Promise<IntegrationTool> {
    const res = await this.client.request<IntegrationTool>({
      method: 'POST',
      path: `/agents/${agentId}/integrations/custom_api/${integrationId}/tools`,
      body,
      ...options,
    });
    return res.data;
  }

  async delete(agentId: string, integrationId: string, toolId: string): Promise<void> {
    await this.client.request<unknown>({
      method: 'DELETE',
      path: `/agents/${agentId}/integrations/custom_api/${integrationId}/tools/${toolId}`,
    });
  }
}

export class AgentCustomApiIntegrations {
  readonly tools: AgentCustomApiTools;

  constructor(private readonly client: RequestExecutor) {
    this.tools = new AgentCustomApiTools(client);
  }

  async list(agentId: string): Promise<readonly CustomApiIntegration[]> {
    const res = await this.client.request<CustomApiIntegration[]>({
      method: 'GET',
      path: `/agents/${agentId}/integrations/custom_api`,
    });
    return res.data;
  }

  async configure(
    agentId: string,
    body: CustomApiConfigureBody,
    options: RequestOptions = {},
  ): Promise<CustomApiIntegration> {
    const res = await this.client.request<CustomApiIntegration>({
      method: 'POST',
      path: `/agents/${agentId}/integrations/custom_api/configure`,
      body,
      ...options,
    });
    return res.data;
  }

  async disconnect(agentId: string, integrationId: string): Promise<void> {
    await this.client.request<unknown>({
      method: 'DELETE',
      path: `/agents/${agentId}/integrations/custom_api/${integrationId}`,
    });
  }
}

export class AgentMcpServerTools {
  constructor(private readonly client: RequestExecutor) {}

  async list(agentId: string, integrationId: string): Promise<readonly IntegrationTool[]> {
    const res = await this.client.request<IntegrationTool[]>({
      method: 'GET',
      path: `/agents/${agentId}/integrations/mcp_server/${integrationId}/tools`,
    });
    return res.data;
  }
}

export class AgentMcpServerIntegrations {
  readonly tools: AgentMcpServerTools;

  constructor(private readonly client: RequestExecutor) {
    this.tools = new AgentMcpServerTools(client);
  }

  async list(agentId: string): Promise<readonly McpServerIntegration[]> {
    const res = await this.client.request<McpServerIntegration[]>({
      method: 'GET',
      path: `/agents/${agentId}/integrations/mcp_server`,
    });
    return res.data;
  }

  async configure(
    agentId: string,
    body: McpServerConfigureBody,
    options: RequestOptions = {},
  ): Promise<McpServerIntegration> {
    const res = await this.client.request<McpServerIntegration>({
      method: 'POST',
      path: `/agents/${agentId}/integrations/mcp_server/configure`,
      body,
      ...options,
    });
    return res.data;
  }

  async disconnect(agentId: string, integrationId: string): Promise<void> {
    await this.client.request<unknown>({
      method: 'DELETE',
      path: `/agents/${agentId}/integrations/mcp_server/${integrationId}`,
    });
  }

  async discover(agentId: string, integrationId: string): Promise<McpServerDiscoverResult> {
    const res = await this.client.request<McpServerDiscoverResult>({
      method: 'POST',
      path: `/agents/${agentId}/integrations/mcp_server/${integrationId}/discover`,
    });
    return res.data;
  }

  async test(agentId: string, integrationId: string): Promise<McpServerTestResult> {
    const res = await this.client.request<McpServerTestResult>({
      method: 'POST',
      path: `/agents/${agentId}/integrations/mcp_server/${integrationId}/test`,
    });
    return res.data;
  }
}

export class AgentPipedreamIntegrations {
  constructor(private readonly client: RequestExecutor) {}

  async list(agentId: string): Promise<readonly PipedreamIntegration[]> {
    const res = await this.client.request<PipedreamIntegration[]>({
      method: 'GET',
      path: `/agents/${agentId}/integrations/pipedream`,
    });
    return res.data;
  }

  async configure(
    agentId: string,
    body: PipedreamConfigureBody,
    options: RequestOptions = {},
  ): Promise<OnboardingUrl> {
    const res = await this.client.request<OnboardingUrl>({
      method: 'POST',
      path: `/agents/${agentId}/integrations/pipedream/configure`,
      body,
      ...options,
    });
    return res.data;
  }

  async disconnect(agentId: string, integrationId: string): Promise<void> {
    await this.client.request<unknown>({
      method: 'DELETE',
      path: `/agents/${agentId}/integrations/pipedream/${integrationId}`,
    });
  }
}

export class AgentIntegrations {
  readonly bimpeai: AgentBimpeaiIntegrations;
  readonly customApi: AgentCustomApiIntegrations;
  readonly mcpServer: AgentMcpServerIntegrations;
  readonly pipedream: AgentPipedreamIntegrations;

  constructor(private readonly client: RequestExecutor) {
    this.bimpeai = new AgentBimpeaiIntegrations(client);
    this.customApi = new AgentCustomApiIntegrations(client);
    this.mcpServer = new AgentMcpServerIntegrations(client);
    this.pipedream = new AgentPipedreamIntegrations(client);
  }

  async list(agentId: string): Promise<readonly AgentIntegration[]> {
    const res = await this.client.request<AgentIntegration[]>({
      method: 'GET',
      path: `/agents/${agentId}/integrations`,
    });
    return res.data;
  }
}
