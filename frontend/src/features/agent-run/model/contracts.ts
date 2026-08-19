import type { SchemaVersion } from '../../../entities/agent-run/model/agentContracts'
import type { AgentRunId } from '../../../entities/agent-run/model/agentRun'

export type SubmitClarificationDraft = Readonly<{
  schemaVersion: SchemaVersion
  runId: AgentRunId
  answers: Readonly<Record<string, string>>
}>
