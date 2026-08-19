import type { AgentRunId } from '../../agent-run/model/agentRun'


export type SkillExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'fallback'

export type SkillExecution = Readonly<{
  id: string
  runId: AgentRunId
  skillName: string
  skillVersion: string
  promptVersion: string
  status: SkillExecutionStatus
  durationMs: number | null
  errorCode: string | null
}>
