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

export type ApiScopeItemDto = Readonly<{
  item_id: string
  title: string
  description: string
  rationale: string
}>

export type ApiScopeDto = Readonly<{
  schema_version: '1.0.0'
  prompt_version: `${number}.${number}.${number}`
  must: ReadonlyArray<ApiScopeItemDto>
  should: ReadonlyArray<ApiScopeItemDto>
  could: ReadonlyArray<ApiScopeItemDto>
  wont: ReadonlyArray<ApiScopeItemDto>
  blocked_by_missing_information: boolean
}>

export type ApiEstimatedTaskDto = Readonly<{
  task_id: string
  title: string
  description: string
  dependencies: ReadonlyArray<string>
  min_hours: string
  max_hours: string
  estimate_basis: string
  acceptance_criteria: ReadonlyArray<string>
}>

export type ApiEstimateDto = Readonly<{
  schema_version: '1.0.0'
  prompt_version: `${number}.${number}.${number}`
  tasks: ReadonlyArray<ApiEstimatedTaskDto>
  buffer_hours: string
  uncertainty_notes: ReadonlyArray<string>
}>

export type ApiRiskReviewDto = Readonly<{
  schema_version: '1.0.0'
  prompt_version: `${number}.${number}.${number}`
  risks: ReadonlyArray<{
    risk_id: string
    category: 'requirement' | 'technical' | 'schedule' | 'privacy' | 'commercial'
    severity: 'low' | 'medium' | 'high'
    cause: string
    impact: string
    mitigation: string
    requires_human_decision: boolean
  }>
  human_decisions: ReadonlyArray<string>
}>

export type ApiQuoteOptionDto = Readonly<{
  tier: 'basic' | 'standard' | 'premium'
  amount: ApiMoneyDto
  included_hours: string
  calculation_summary: string
}>

export type ApiPricingDto = Readonly<{
  schema_version: '1.0.0'
  policy_version: `${number}.${number}.${number}`
  options: readonly [ApiQuoteOptionDto, ApiQuoteOptionDto, ApiQuoteOptionDto]
}>

export type ApiProposalDto = Readonly<{
  schema_version: '1.0.0'
  prompt_version: `${number}.${number}.${number}`
  document_status: 'ai_draft'
  project_summary: string
  deliverables: ReadonlyArray<string>
  exclusions: ReadonlyArray<string>
  acceptance_criteria: ReadonlyArray<string>
  quote_options: readonly [ApiQuoteOptionDto, ApiQuoteOptionDto, ApiQuoteOptionDto]
  disclaimers: ReadonlyArray<string>
  requires_human_approval: true
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
  scope: ApiScopeDto | null
  estimate: ApiEstimateDto | null
  risk_review: ApiRiskReviewDto | null
  pricing: ApiPricingDto | null
  proposal: ApiProposalDto | null
  clarification_approved: boolean
  quote_approved: boolean
  selected_quote_tier: 'basic' | 'standard' | 'premium' | null
  retrieved_context: ReadonlyArray<{
    source_id: string
    title: string
    excerpt: string
    score: number
  }>
  execution_mode: 'model' | 'rule_fallback'
  model_name: string | null
  fallback_reason: string | null
  model_input_tokens: number | null
  model_output_tokens: number | null
  model_latency_ms: number | null
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
