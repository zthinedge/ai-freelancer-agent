import type { Money } from '../../../entities/project/model/project'


export type ProjectIntakeDraft = Readonly<{
  name: string
  clientRequest: string
  serviceType: string
  budget: Money | null
  deadline: string | null
  hourlyRate: Money
}>
