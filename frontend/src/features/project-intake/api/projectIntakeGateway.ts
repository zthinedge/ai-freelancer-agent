import type { ProjectAnalysis } from '../../../entities/project-analysis/model/projectAnalysis'
import type { ProjectIntakeDraft } from '../model/contracts'


export interface ProjectIntakeGateway {
  createProject(draft: ProjectIntakeDraft): Promise<ProjectAnalysis>
}
