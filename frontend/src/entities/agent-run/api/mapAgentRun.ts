import type { ApiAgentRunDto, ApiAgentStateDto } from '../../../shared/api/projectDtos'
import type {
  AgentState,
  ClarificationPlannerOutput,
  ClarificationQuestion,
  ConfirmedFact,
  RequirementIntakeOutput,
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
    scope: null,
    estimate: null,
    riskReview: null,
    pricing: null,
    proposal: null,
    clarificationApproved: state.clarification_approved,
    quoteApproved: state.quote_approved,
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
