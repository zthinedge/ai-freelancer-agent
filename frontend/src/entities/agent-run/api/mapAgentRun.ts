import type { ApiAgentRunDto, ApiAgentStateDto } from '../../../shared/api/projectDtos'
import type {
  AgentState,
  ClarificationPlannerOutput,
  ClarificationQuestion,
  ConfirmedFact,
  RequirementIntakeOutput,
  ScopeDesignerOutput,
  TaskEstimatorOutput,
  RiskReviewerOutput,
  PricingToolOutput,
  ProposalWriterOutput,
  QuoteOption,
} from '../model/agentContracts'
import type { AgentRun } from '../model/agentRun'

function mapFact(fact: ApiAgentStateDto['confirmed_facts'][number]): ConfirmedFact {
  return {
    field: fact.field,
    value: fact.value,
    source: fact.source,
    evidence: fact.evidence,
  }
}

function mapQuestion(question: ApiAgentStateDto['pending_questions'][number]): ClarificationQuestion {
  return {
    questionId: question.question_id,
    field: question.field,
    question: question.question,
    reason: question.reason,
    priority: question.priority,
  }
}

function mapIntake(intake: NonNullable<ApiAgentStateDto['intake']>): RequirementIntakeOutput {
  return {
    schemaVersion: intake.schema_version,
    promptVersion: intake.prompt_version,
    projectType: intake.project_type,
    goals: intake.goals,
    targetUsers: intake.target_users,
    confirmedFacts: intake.confirmed_facts.map(mapFact),
    missingFields: intake.missing_fields,
    assumptions: intake.assumptions.map((assumption) => ({
      field: assumption.field,
      proposedValue: assumption.proposed_value,
      reason: assumption.reason,
    })),
  }
}

function mapClarification(
  clarification: NonNullable<ApiAgentStateDto['clarification']>,
): ClarificationPlannerOutput {
  return {
    schemaVersion: clarification.schema_version,
    promptVersion: clarification.prompt_version,
    questions: clarification.questions.map(mapQuestion),
    requiresHumanInput: true,
  }
}

function mapScope(scope: NonNullable<ApiAgentStateDto['scope']>): ScopeDesignerOutput {
  const mapItem = (item: (typeof scope.must)[number]) => ({
    itemId: item.item_id,
    title: item.title,
    description: item.description,
    rationale: item.rationale,
  })
  return {
    schemaVersion: scope.schema_version,
    promptVersion: scope.prompt_version,
    must: scope.must.map(mapItem),
    should: scope.should.map(mapItem),
    could: scope.could.map(mapItem),
    wont: scope.wont.map(mapItem),
    blockedByMissingInformation: scope.blocked_by_missing_information,
  }
}

function mapEstimate(estimate: NonNullable<ApiAgentStateDto['estimate']>): TaskEstimatorOutput {
  return {
    schemaVersion: estimate.schema_version,
    promptVersion: estimate.prompt_version,
    tasks: estimate.tasks.map((task) => ({
      taskId: task.task_id,
      title: task.title,
      description: task.description,
      dependencies: task.dependencies,
      minHours: task.min_hours,
      maxHours: task.max_hours,
      estimateBasis: task.estimate_basis,
      acceptanceCriteria: task.acceptance_criteria,
    })),
    bufferHours: estimate.buffer_hours,
    uncertaintyNotes: estimate.uncertainty_notes,
  }
}

function mapRiskReview(riskReview: NonNullable<ApiAgentStateDto['risk_review']>): RiskReviewerOutput {
  return {
    schemaVersion: riskReview.schema_version,
    promptVersion: riskReview.prompt_version,
    risks: riskReview.risks.map((risk) => ({
      riskId: risk.risk_id,
      category: risk.category,
      severity: risk.severity,
      cause: risk.cause,
      impact: risk.impact,
      mitigation: risk.mitigation,
      requiresHumanDecision: risk.requires_human_decision,
    })),
    humanDecisions: riskReview.human_decisions,
  }
}

function mapQuoteOption(option: NonNullable<ApiAgentStateDto['pricing']>['options'][number]): QuoteOption {
  return {
    tier: option.tier,
    amount: option.amount,
    includedHours: option.included_hours,
    calculationSummary: option.calculation_summary,
  }
}

function mapPricing(pricing: NonNullable<ApiAgentStateDto['pricing']>): PricingToolOutput {
  return {
    schemaVersion: pricing.schema_version,
    policyVersion: pricing.policy_version,
    options: [
      mapQuoteOption(pricing.options[0]),
      mapQuoteOption(pricing.options[1]),
      mapQuoteOption(pricing.options[2]),
    ],
  }
}

function mapProposal(proposal: NonNullable<ApiAgentStateDto['proposal']>): ProposalWriterOutput {
  return {
    schemaVersion: proposal.schema_version,
    promptVersion: proposal.prompt_version,
    documentStatus: proposal.document_status,
    projectSummary: proposal.project_summary,
    deliverables: proposal.deliverables,
    exclusions: proposal.exclusions,
    acceptanceCriteria: proposal.acceptance_criteria,
    quoteOptions: [
      mapQuoteOption(proposal.quote_options[0]),
      mapQuoteOption(proposal.quote_options[1]),
      mapQuoteOption(proposal.quote_options[2]),
    ],
    disclaimers: proposal.disclaimers,
    requiresHumanApproval: proposal.requires_human_approval,
  }
}

function mapState(state: ApiAgentStateDto): AgentState {
  return {
    schemaVersion: state.schema_version,
    runId: state.run_id,
    projectId: state.project_id,
    status: state.status,
    currentStep: state.current_step,
    confirmedFacts: state.confirmed_facts.map(mapFact),
    pendingQuestions: state.pending_questions.map(mapQuestion),
    intake: state.intake === null ? null : mapIntake(state.intake),
    clarification: state.clarification === null ? null : mapClarification(state.clarification),
    scope: state.scope === null ? null : mapScope(state.scope),
    estimate: state.estimate === null ? null : mapEstimate(state.estimate),
    riskReview: state.risk_review === null ? null : mapRiskReview(state.risk_review),
    pricing: state.pricing === null ? null : mapPricing(state.pricing),
    proposal: state.proposal === null ? null : mapProposal(state.proposal),
    clarificationApproved: state.clarification_approved,
    quoteApproved: state.quote_approved,
    selectedQuoteTier: state.selected_quote_tier,
    retrievedContext: state.retrieved_context.map((item) => ({
      sourceId: item.source_id,
      title: item.title,
      excerpt: item.excerpt,
      score: item.score,
    })),
    executionMode: state.execution_mode,
    modelName: state.model_name,
    fallbackReason: state.fallback_reason,
    modelInputTokens: state.model_input_tokens,
    modelOutputTokens: state.model_output_tokens,
    modelLatencyMs: state.model_latency_ms,
  }
}

export function mapAgentRun(run: ApiAgentRunDto): AgentRun {
  return {
    id: run.id,
    projectId: run.project_id,
    status: run.status,
    currentStep: run.current_step,
    state: mapState(run.state),
  }
}
