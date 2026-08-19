export type ApiMoneyDto = Readonly<{
  amount: string
  currency: 'CNY'
}>

type ApiServiceType =
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

type ApiAgentRunStatus =
  | 'pending'
  | 'running'
  | 'waiting_user'
  | 'waiting_approval'
  | 'completed'
  | 'failed'

type ApiWorkflowStep =
  | 'requirement_intake'
  | 'clarification_planner'
  | 'scope_designer'
  | 'task_estimator'
  | 'risk_reviewer'
  | 'pricing_calculator'
  | 'proposal_writer'

export type ApiConfirmedFactDto = Readonly<{
  field: string
  value: string
  source: 'client_request' | 'clarification_answer' | 'system'
  evidence: string
}>

export type ApiClarificationQuestionDto = Readonly<{
  question_id: string
  field: string
  question: string
  reason: string
  priority: 'critical' | 'important' | 'optional'
}>

export type ApiIntakeDto = Readonly<{
  schema_version: '1.0.0'
  prompt_version: `${number}.${number}.${number}`
  project_type: ApiServiceType
  goals: ReadonlyArray<string>
  target_users: ReadonlyArray<string>
  confirmed_facts: ReadonlyArray<ApiConfirmedFactDto>
  missing_fields: ReadonlyArray<string>
  assumptions: ReadonlyArray<{
    field: string
    proposed_value: string
    reason: string
  }>
}>

export type ApiClarificationDto = Readonly<{
  schema_version: '1.0.0'
  prompt_version: `${number}.${number}.${number}`
  questions: ReadonlyArray<ApiClarificationQuestionDto>
  requires_human_input: true
}>

export type ApiAgentStateDto = Readonly<{
  schema_version: '1.0.0'
  run_id: string
  project_id: string
  status: ApiAgentRunStatus
  current_step: ApiWorkflowStep | null
  confirmed_facts: ReadonlyArray<ApiConfirmedFactDto>
  pending_questions: ReadonlyArray<ApiClarificationQuestionDto>
  intake: ApiIntakeDto | null
  clarification: ApiClarificationDto | null
  scope: unknown
  estimate: unknown
  risk_review: unknown
  pricing: unknown
  proposal: unknown
  clarification_approved: boolean
  quote_approved: boolean
}>

export type ApiAgentRunDto = Readonly<{
  schema_version: '1.0.0'
  id: string
  project_id: string
  status: ApiAgentRunStatus
  current_step: ApiWorkflowStep | null
  state: ApiAgentStateDto
}>

export type ApiProjectDto = Readonly<{
  schema_version: '1.0.0'
  id: string
  name: string
  client_request: string
  service_type: ApiServiceType
  budget: ApiMoneyDto | null
  deadline: string | null
  hourly_rate: ApiMoneyDto
  created_at: string
  updated_at: string
  run: ApiAgentRunDto | null
}>
