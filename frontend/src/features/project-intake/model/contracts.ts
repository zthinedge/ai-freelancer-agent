import type { SchemaVersion } from '../../../entities/agent-run/model/agentContracts'
import type { Money, ServiceType } from '../../../entities/project/model/project'


export type ProjectIntakeDraft = Readonly<{
  schemaVersion: SchemaVersion
  name: string
  clientRequest: string
  serviceType: ServiceType
  budget: Money | null
  deadline: string | null
  hourlyRate: Money
}>
