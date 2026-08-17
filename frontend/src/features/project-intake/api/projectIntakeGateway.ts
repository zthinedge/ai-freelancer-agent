import type { AgentRun } from '../../../entities/agent-run/model/agentRun'
import type { ProjectIntakeDraft } from '../model/contracts'


export interface ProjectIntakeGateway {
  createProject(draft: ProjectIntakeDraft): Promise<AgentRun>
}
