import { mapAgentRun } from '../../../entities/agent-run/api/mapAgentRun'
import type { AgentRun, AgentRunId } from '../../../entities/agent-run/model/agentRun'
import { httpClient } from '../../../shared/api/client'
import type { ApiAgentRunDto } from '../../../shared/api/projectDtos'
import type { AgentRunGateway } from './agentRunGateway'
import type { SubmitClarificationDraft } from '../model/contracts'

class HttpAgentRunGateway implements AgentRunGateway {
  async getRun(runId: AgentRunId): Promise<AgentRun> {
    const response = await httpClient.request<ApiAgentRunDto>({
      path: `/api/v1/agent-runs/${runId}`,
      method: 'GET',
    })
    return mapAgentRun(response)
  }

  async submitAnswers(command: SubmitClarificationDraft): Promise<AgentRun> {
    const response = await httpClient.request<ApiAgentRunDto>({
      path: `/api/v1/agent-runs/${command.runId}/answers`,
      method: 'POST',
      body: {
        schema_version: command.schemaVersion,
        answers: command.answers,
      },
    })
    return mapAgentRun(response)
  }
}

export const agentRunGateway: AgentRunGateway = new HttpAgentRunGateway()
