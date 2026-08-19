import type { ProjectAnalysis } from '../../../entities/project-analysis/model/projectAnalysis'

export interface ProjectListGateway {
  listProjects(): Promise<ReadonlyArray<ProjectAnalysis>>
}
