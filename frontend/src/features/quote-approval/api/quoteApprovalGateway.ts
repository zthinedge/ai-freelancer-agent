import type { AgentRun, AgentRunId } from '../../../entities/agent-run/model/agentRun'


export interface QuoteApprovalGateway {
  approve(runId: AgentRunId, note?: string): Promise<AgentRun>
  reject(runId: AgentRunId, note: string): Promise<AgentRun>
}
