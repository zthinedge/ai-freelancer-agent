import type { AgentRun, AgentRunId } from '../../../entities/agent-run/model/agentRun'
import type { SkillExecution } from '../../../entities/skill-execution/model/skillExecution'


export interface AgentRunGateway {
  getRun(runId: AgentRunId): Promise<AgentRun>
  listExecutions(runId: AgentRunId): Promise<ReadonlyArray<SkillExecution>>
  submitAnswers(runId: AgentRunId, answers: Readonly<Record<string, string>>): Promise<AgentRun>
}
