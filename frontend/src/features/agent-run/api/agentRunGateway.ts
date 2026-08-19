import type { AgentRun, AgentRunId } from '../../../entities/agent-run/model/agentRun'
import type { SubmitClarificationDraft } from '../model/contracts'


export interface AgentRunGateway {
  getRun(runId: AgentRunId): Promise<AgentRun>
  submitAnswers(command: SubmitClarificationDraft): Promise<AgentRun>
}
