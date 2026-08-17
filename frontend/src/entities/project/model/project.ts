export type ProjectId = string

export type Money = Readonly<{
  amount: string
  currency: 'CNY'
}>

export type Project = Readonly<{
  id: ProjectId
  name: string
  clientRequest: string
  serviceType: string
  budget: Money | null
  deadline: string | null
  hourlyRate: Money
  createdAt: string
  updatedAt: string
}>
