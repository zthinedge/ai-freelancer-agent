import type { ApiProjectDto } from '../../../shared/api/projectDtos'
import { mapAgentRun } from '../../agent-run/api/mapAgentRun'
import type { ProjectAnalysis } from '../model/projectAnalysis'

export function mapProjectAnalysis(project: ApiProjectDto): ProjectAnalysis {
  return {
    id: project.id,
    name: project.name,
    clientRequest: project.client_request,
    serviceType: project.service_type,
    budget: project.budget,
    deadline: project.deadline,
    hourlyRate: project.hourly_rate,
    createdAt: project.created_at,
    updatedAt: project.updated_at,
    run: project.run === null ? null : mapAgentRun(project.run),
  }
}
