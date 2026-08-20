import { httpClient } from './client'

export type AiRuntimeStatus = Readonly<{
  mode: 'model' | 'rule_fallback'
  model: string
  memoryBackend: 'sqlite'
  ragEnabled: boolean
  mcpEnabled: boolean
}>

type ApiHealthResponse = Readonly<{
  status: 'ok'
  version: string
  environment: string
  architecture: 'modular-monolith'
  ai_mode: 'model' | 'rule_fallback'
  ai_model: string
  memory_backend: 'sqlite'
  rag_enabled: boolean
  mcp_enabled: boolean
}>

export async function getSystemStatus(): Promise<AiRuntimeStatus> {
  const response = await httpClient.request<ApiHealthResponse>({
    path: '/api/health',
    method: 'GET',
  })
  return {
    mode: response.ai_mode,
    model: response.ai_model,
    memoryBackend: response.memory_backend,
    ragEnabled: response.rag_enabled,
    mcpEnabled: response.mcp_enabled,
  }
}
