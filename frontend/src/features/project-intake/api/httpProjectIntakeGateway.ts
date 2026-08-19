import { mapProjectAnalysis } from '../../../entities/project-analysis/api/mapProjectAnalysis'
import type { ProjectAnalysis } from '../../../entities/project-analysis/model/projectAnalysis'
import { httpClient } from '../../../shared/api/client'
import type { ApiProjectDto } from '../../../shared/api/projectDtos'
import type { ProjectIntakeGateway } from './projectIntakeGateway'
import type { ProjectIntakeDraft } from '../model/contracts'

class HttpProjectIntakeGateway implements ProjectIntakeGateway {
  async createProject(draft: ProjectIntakeDraft): Promise<ProjectAnalysis> {
    const response = await httpClient.request<ApiProjectDto>({
      path: '/api/v1/projects',
      method: 'POST',
      body: {
        schema_version: draft.schemaVersion,
        name: draft.name,
        client_request: draft.clientRequest,
        service_type: draft.serviceType,
        budget: draft.budget,
        deadline: draft.deadline,
        hourly_rate: draft.hourlyRate,
      },
    })
    return mapProjectAnalysis(response)
  }
}

export const projectIntakeGateway: ProjectIntakeGateway = new HttpProjectIntakeGateway()
