import type { AgentRun } from '../../../entities/agent-run/model/agentRun'
import type { QuoteApprovalDraft } from '../model/contracts'


export interface QuoteApprovalGateway {
  submit(command: QuoteApprovalDraft): Promise<AgentRun>
}
