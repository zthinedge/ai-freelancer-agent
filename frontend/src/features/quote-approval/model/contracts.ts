import type { SchemaVersion } from '../../../entities/agent-run/model/agentContracts'
import type { AgentRunId } from '../../../entities/agent-run/model/agentRun'

export type QuoteApprovalDraft = Readonly<{
  schemaVersion: SchemaVersion
  runId: AgentRunId
  approved: boolean
  note: string | null
}>
