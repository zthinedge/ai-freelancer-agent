import type { ProjectAnalysis } from '../../../entities/project-analysis/model/projectAnalysis'
import { getServicePresentation } from '../../../entities/project/model/serviceType'

type ProjectCardProps = Readonly<{
  project: ProjectAnalysis
  isSelected: boolean
  onSelect: (project: ProjectAnalysis) => void
}>

const statusLabels = {
  pending: '待开始',
  running: '分析中',
  waiting_user: '待补充',
  waiting_approval: '待确认',
  completed: '已澄清',
  failed: '失败',
} as const

export function ProjectCard({ project, isSelected, onSelect }: ProjectCardProps) {
  const service = getServicePresentation(project.serviceType)
  const status = project.run?.status ?? 'pending'
  const factCount = project.run?.state.confirmedFacts.length ?? 0
  const questionCount = project.run?.state.pendingQuestions.length ?? 0
  const date = new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric' }).format(
    new Date(project.createdAt),
  )

  return (
    <button
      className={isSelected ? 'project-card selected' : 'project-card'}
      type="button"
      onClick={() => onSelect(project)}
      aria-pressed={isSelected}
    >
      <span className={`project-visual tone-${service.tone}`}>
        <span className="visual-topline">
          <i>{service.symbol}</i>
          <b>{service.label}</b>
        </span>
        <strong>{project.name}</strong>
        <span className="visual-metric">
          <b>{factCount}</b>
          <small>已知事实</small>
        </span>
        <span className="visual-metric">
          <b>{questionCount}</b>
          <small>待确认</small>
        </span>
        <i className="visual-shape" />
      </span>
      <span className="project-card-body">
        <span className="project-card-meta">
          <i className={`status-dot ${status}`} />
          {statusLabels[status]}
          <time>{date}</time>
        </span>
        <strong>{project.name}</strong>
        <span className="request-preview">{project.clientRequest}</span>
        <span className="card-footer">
          <span>{project.deadline ?? '期限待确认'}</span>
          <b>{project.budget === null ? '预算待确认' : `¥${project.budget.amount}`}</b>
        </span>
      </span>
    </button>
  )
}
