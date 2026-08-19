export type ProjectId = string

export type ServiceType =
  | 'auto_detect'
  | 'website'
  | 'ai_application'
  | 'ecommerce'
  | 'presentation'
  | 'content'
  | 'design'
  | 'data_analysis'
  | 'video'
  | 'other'

export type Money = Readonly<{
  amount: string
  currency: 'CNY'
}>

export type Project = Readonly<{
  id: ProjectId
  name: string
  clientRequest: string
  serviceType: ServiceType
  budget: Money | null
  deadline: string | null
  hourlyRate: Money
  createdAt: string
  updatedAt: string
}>
