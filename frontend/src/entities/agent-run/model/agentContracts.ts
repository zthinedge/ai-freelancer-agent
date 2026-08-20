import type { Money, ServiceType } from '../../project/model/project'

export type SchemaVersion = '1.0.0'
export type SemanticVersion = `${number}.${number}.${number}`
export type FactSource = 'client_request' | 'clarification_answer' | 'system'
export type QuestionPriority = 'critical' | 'important' | 'optional'
export type RiskSeverity = 'low' | 'medium' | 'high'
export type QuoteTier = 'basic' | 'standard' | 'premium'

export type ProjectBrief = Readonly<{
  schemaVersion: SchemaVersion
  name: string
  clientRequest: string
  serviceType: ServiceType
  budget: Money | null
  deadline: string | null
  hourlyRate: Money
}>

export type RequirementIntakeInput = ProjectBrief

export type ConfirmedFact = Readonly<{
  field: string
  value: string
  source: FactSource
  evidence: string
}>

export type UncertainAssumption = Readonly<{
  field: string
  proposedValue: string
  reason: string
}>

export type RequirementIntakeOutput = Readonly<{
  schemaVersion: SchemaVersion
  promptVersion: SemanticVersion
  projectType: ServiceType
  goals: ReadonlyArray<string>
  targetUsers: ReadonlyArray<string>
  confirmedFacts: ReadonlyArray<ConfirmedFact>
  missingFields: ReadonlyArray<string>
  assumptions: ReadonlyArray<UncertainAssumption>
}>

export type ClarificationQuestion = Readonly<{
  questionId: string
  field: string
  question: string
  reason: string
  priority: QuestionPriority
}>

export type ClarificationPlannerInput = Readonly<{
  schemaVersion: SchemaVersion
  projectType: ServiceType
  confirmedFacts: ReadonlyArray<ConfirmedFact>
  missingFields: ReadonlyArray<string>
  clientConstraints: ReadonlyArray<string>
}>

export type ClarificationPlannerOutput = Readonly<{
  schemaVersion: SchemaVersion
  promptVersion: SemanticVersion
  questions: ReadonlyArray<ClarificationQuestion>
  requiresHumanInput: true
}>

export type ScopeItem = Readonly<{
  itemId: string
  title: string
  description: string
  rationale: string
}>

export type ScopeDesignerInput = Readonly<{
  schemaVersion: SchemaVersion
  confirmedFacts: ReadonlyArray<ConfirmedFact>
  clarificationAnswers: Readonly<Record<string, string>>
}>

export type ScopeDesignerOutput = Readonly<{
  schemaVersion: SchemaVersion
  promptVersion: SemanticVersion
  must: ReadonlyArray<ScopeItem>
  should: ReadonlyArray<ScopeItem>
  could: ReadonlyArray<ScopeItem>
  wont: ReadonlyArray<ScopeItem>
  blockedByMissingInformation: boolean
}>

export type EstimatedTask = Readonly<{
  taskId: string
  title: string
  description: string
  dependencies: ReadonlyArray<string>
  minHours: string
  maxHours: string
  estimateBasis: string
  acceptanceCriteria: ReadonlyArray<string>
}>

export type TaskEstimatorInput = Readonly<{
  schemaVersion: SchemaVersion
  scope: ScopeDesignerOutput
  acceptanceStandards: ReadonlyArray<string>
  deadline: string | null
  externalConstraints: ReadonlyArray<string>
}>

export type TaskEstimatorOutput = Readonly<{
  schemaVersion: SchemaVersion
  promptVersion: SemanticVersion
  tasks: ReadonlyArray<EstimatedTask>
  bufferHours: string
  uncertaintyNotes: ReadonlyArray<string>
}>

export type RiskItem = Readonly<{
  riskId: string
  category: 'requirement' | 'technical' | 'schedule' | 'privacy' | 'commercial'
  severity: RiskSeverity
  cause: string
  impact: string
  mitigation: string
  requiresHumanDecision: boolean
}>

export type RiskReviewerInput = Readonly<{
  schemaVersion: SchemaVersion
  scope: ScopeDesignerOutput
  estimate: TaskEstimatorOutput
  clientConstraints: ReadonlyArray<string>
  externalDependencies: ReadonlyArray<string>
}>

export type RiskReviewerOutput = Readonly<{
  schemaVersion: SchemaVersion
  promptVersion: SemanticVersion
  risks: ReadonlyArray<RiskItem>
  humanDecisions: ReadonlyArray<string>
}>

export type QuoteOption = Readonly<{
  tier: QuoteTier
  amount: Money
  includedHours: string
  calculationSummary: string
}>

export type PricingToolInput = Readonly<{
  schemaVersion: SchemaVersion
  minHours: string
  maxHours: string
  hourlyRate: Money
  contingencyRate: string
}>

export type PricingToolOutput = Readonly<{
  schemaVersion: SchemaVersion
  policyVersion: SemanticVersion
  options: readonly [QuoteOption, QuoteOption, QuoteOption]
}>

export type ProposalWriterOutput = Readonly<{
  schemaVersion: SchemaVersion
  promptVersion: SemanticVersion
  documentStatus: 'ai_draft'
  projectSummary: string
  deliverables: ReadonlyArray<string>
  exclusions: ReadonlyArray<string>
  acceptanceCriteria: ReadonlyArray<string>
  quoteOptions: readonly [QuoteOption, QuoteOption, QuoteOption]
  disclaimers: ReadonlyArray<string>
  requiresHumanApproval: true
}>

export type ProposalWriterInput = Readonly<{
  schemaVersion: SchemaVersion
  projectName: string
  scope: ScopeDesignerOutput
  estimate: TaskEstimatorOutput
  riskReview: RiskReviewerOutput
  pricing: PricingToolOutput
}>

export type SkillInput =
  | RequirementIntakeInput
  | ClarificationPlannerInput
  | ScopeDesignerInput
  | TaskEstimatorInput
  | RiskReviewerInput
  | ProposalWriterInput

export type SkillOutput =
  | RequirementIntakeOutput
  | ClarificationPlannerOutput
  | ScopeDesignerOutput
  | TaskEstimatorOutput
  | RiskReviewerOutput
  | ProposalWriterOutput

export type AgentState = Readonly<{
  schemaVersion: SchemaVersion
  runId: string
  projectId: string
  status: import('./agentRun').AgentRunStatus
  currentStep: import('./agentRun').WorkflowStep | null
  confirmedFacts: ReadonlyArray<ConfirmedFact>
  pendingQuestions: ReadonlyArray<ClarificationQuestion>
  intake: RequirementIntakeOutput | null
  clarification: ClarificationPlannerOutput | null
  scope: ScopeDesignerOutput | null
  estimate: TaskEstimatorOutput | null
  riskReview: RiskReviewerOutput | null
  pricing: PricingToolOutput | null
  proposal: ProposalWriterOutput | null
  clarificationApproved: boolean
  quoteApproved: boolean
  selectedQuoteTier: QuoteTier | null
  retrievedContext: ReadonlyArray<{
    sourceId: string
    title: string
    excerpt: string
    score: number
  }>
  executionMode: 'model' | 'rule_fallback'
  modelName: string | null
  fallbackReason: string | null
  modelInputTokens: number | null
  modelOutputTokens: number | null
  modelLatencyMs: number | null
}>
