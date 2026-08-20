import type { SchemaVersion } from '../../../entities/agent-run/model/agentContracts'
import type { QuoteTier } from '../../../entities/agent-run/model/agentContracts'
import type { AgentRunId } from '../../../entities/agent-run/model/agentRun'

export type QuoteApprovalDraft = Readonly<{
  schemaVersion: SchemaVersion
  runId: AgentRunId
  approved: boolean
  selectedTier: QuoteTier | null
  note: string | null
}>
