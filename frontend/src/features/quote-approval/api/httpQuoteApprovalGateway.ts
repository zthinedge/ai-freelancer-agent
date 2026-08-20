import { mapAgentRun } from '../../../entities/agent-run/api/mapAgentRun'
import type { AgentRun } from '../../../entities/agent-run/model/agentRun'
import { httpClient } from '../../../shared/api/client'
import type { ApiAgentRunDto } from '../../../shared/api/projectDtos'
import type { QuoteApprovalGateway } from './quoteApprovalGateway'
import type { QuoteApprovalDraft } from '../model/contracts'

class HttpQuoteApprovalGateway implements QuoteApprovalGateway {
  async submit(command: QuoteApprovalDraft): Promise<AgentRun> {
    const response = await httpClient.request<ApiAgentRunDto>({
      path: `/api/v1/agent-runs/${command.runId}/approve`,
      method: 'POST',
      body: {
        schema_version: command.schemaVersion,
        approved: command.approved,
        selected_tier: command.selectedTier,
        note: command.note,
      },
    })
    return mapAgentRun(response)
  }
}

export const quoteApprovalGateway: QuoteApprovalGateway = new HttpQuoteApprovalGateway()
