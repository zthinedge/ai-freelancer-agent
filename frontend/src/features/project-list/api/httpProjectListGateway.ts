import { mapProjectAnalysis } from '../../../entities/project-analysis/api/mapProjectAnalysis'
import type { ProjectAnalysis } from '../../../entities/project-analysis/model/projectAnalysis'
import { httpClient } from '../../../shared/api/client'
import type { ApiProjectDto } from '../../../shared/api/projectDtos'
import type { ProjectListGateway } from './projectListGateway'

class HttpProjectListGateway implements ProjectListGateway {
  async listProjects(): Promise<ReadonlyArray<ProjectAnalysis>> {
    const response = await httpClient.request<ReadonlyArray<ApiProjectDto>>({
      path: '/api/v1/projects',
      method: 'GET',
    })
    return response.map(mapProjectAnalysis)
  }
}

export const projectListGateway: ProjectListGateway = new HttpProjectListGateway()
