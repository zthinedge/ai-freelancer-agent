import type { ProjectId } from '../../project/model/project'


export type AgentRunId = string

export type AgentRunStatus =
  | 'pending'
  | 'running'
  | 'waiting_user'
  | 'waiting_approval'
  | 'completed'
  | 'failed'

export type WorkflowStep =
  | 'requirement_intake'
  | 'clarification_planner'
  | 'scope_designer'
  | 'task_estimator'
  | 'risk_reviewer'
  | 'pricing_calculator'
  | 'proposal_writer'

export type AgentRun = Readonly<{
  id: AgentRunId
  projectId: ProjectId
  status: AgentRunStatus
  currentStep: WorkflowStep | null
  state: Readonly<Record<string, unknown>>
}>
