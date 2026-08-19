import type { AgentRun } from '../../agent-run/model/agentRun'
import type { Project } from '../../project/model/project'

export type ProjectAnalysis = Project &
  Readonly<{
    run: AgentRun | null
  }>
