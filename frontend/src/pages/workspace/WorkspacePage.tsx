import { useCallback, useDeferredValue, useEffect, useMemo, useState } from 'react'

import type { ProjectAnalysis } from '../../entities/project-analysis/model/projectAnalysis'
import { SERVICE_PRESENTATIONS } from '../../entities/project/model/serviceType'
import type { ServiceType } from '../../entities/project/model/project'
import { agentRunGateway } from '../../features/agent-run/api/httpAgentRunGateway'
import { AnalysisPanel } from '../../features/agent-run/ui/AnalysisPanel'
import { projectIntakeGateway } from '../../features/project-intake/api/httpProjectIntakeGateway'
import type { ProjectIntakeDraft } from '../../features/project-intake/model/contracts'
import { ProjectComposer } from '../../features/project-intake/ui/ProjectComposer'
import { projectListGateway } from '../../features/project-list/api/httpProjectListGateway'
import { ProjectCard } from '../../features/project-list/ui/ProjectCard'
import { HttpError } from '../../shared/api/fetchHttpClient'
import { RefreshIcon } from '../../shared/ui/Icons'

type WorkspacePageProps = Readonly<{
  searchValue: string
  focusSignal: number
  onApiStatusChange: (status: 'checking' | 'connected' | 'offline') => void
}>

export function WorkspacePage({ searchValue, focusSignal, onApiStatusChange }: WorkspacePageProps) {
  const deferredSearch = useDeferredValue(searchValue.trim().toLocaleLowerCase())
  const [projects, setProjects] = useState<ReadonlyArray<ProjectAnalysis>>([])
  const [selectedProject, setSelectedProject] = useState<ProjectAnalysis | null>(null)
  const [activeService, setActiveService] = useState<ServiceType>('auto_detect')
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [isAnswering, setIsAnswering] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadProjects = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const items = await projectListGateway.listProjects()
      onApiStatusChange('connected')
      setProjects(items)
      setSelectedProject((current) => {
        if (current === null) return items[0] ?? null
        return items.find((item) => item.id === current.id) ?? items[0] ?? null
      })
    } catch (requestError) {
      onApiStatusChange(requestError instanceof TypeError ? 'offline' : 'connected')
      setError(toMessage(requestError))
    } finally {
      setIsLoading(false)
    }
  }, [onApiStatusChange])

  useEffect(() => {
    void loadProjects()
  }, [loadProjects])

  const visibleProjects = useMemo(
    () =>
      projects.filter((project) => {
        const matchesService =
          activeService === 'auto_detect' || project.serviceType === activeService
        const haystack = `${project.name} ${project.clientRequest} ${project.serviceType}`.toLocaleLowerCase()
        return matchesService && (!deferredSearch || haystack.includes(deferredSearch))
      }),
    [activeService, deferredSearch, projects],
  )

  const handleCreate = async (draft: ProjectIntakeDraft) => {
    setIsCreating(true)
    setError(null)
    try {
      const project = await projectIntakeGateway.createProject(draft)
      onApiStatusChange('connected')
      setProjects((current) => [project, ...current])
      setSelectedProject(project)
      window.setTimeout(() => {
        document.querySelector('.analysis-panel')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }, 80)
    } catch (requestError) {
      onApiStatusChange(requestError instanceof TypeError ? 'offline' : 'connected')
      setError(toMessage(requestError))
    } finally {
      setIsCreating(false)
    }
  }

  const handleSubmitAnswers = async (answers: Readonly<Record<string, string>>) => {
    if (selectedProject === null || selectedProject.run === null) return
    setIsAnswering(true)
    setError(null)
    try {
      const run = await agentRunGateway.submitAnswers({
        schemaVersion: '1.0.0',
        runId: selectedProject.run.id,
        answers,
      })
      onApiStatusChange('connected')
      const updated = { ...selectedProject, run, updatedAt: new Date().toISOString() }
      setSelectedProject(updated)
      setProjects((current) => current.map((project) => (project.id === updated.id ? updated : project)))
    } catch (requestError) {
      onApiStatusChange(requestError instanceof TypeError ? 'offline' : 'connected')
      setError(toMessage(requestError))
    } finally {
      setIsAnswering(false)
    }
  }

  return (
    <div className="workspace-page" id="top">
      <section className="welcome-strip">
        <div>
          <p className="eyebrow">AI-NATIVE FREELANCER WORKSPACE</p>
          <h1>把模糊需求，变成敢于确认的项目边界。</h1>
          <p>Agent 负责发现信息缺口，你负责最终判断。当前运行在可测试的规则回退模式。</p>
        </div>
        <div className="welcome-stats" aria-label="项目统计">
          <span><b>{projects.length}</b><small>项目档案</small></span>
          <span><b>{projects.filter((item) => item.run?.status === 'waiting_user').length}</b><small>等待补充</small></span>
          <span><b>10</b><small>固定评测</small></span>
        </div>
      </section>

      {error ? (
        <div className="error-banner" role="alert">
          <span>{error}</span>
          <button type="button" onClick={() => setError(null)}>关闭</button>
        </div>
      ) : null}

      <div className="workspace-grid">
        <ProjectComposer focusSignal={focusSignal} isSubmitting={isCreating} onSubmit={handleCreate} />
        <AnalysisPanel
          project={selectedProject}
          isSubmitting={isAnswering}
          onSubmitAnswers={handleSubmitAnswers}
          onClose={() => setSelectedProject(null)}
        />
      </div>

      <section className="project-section" id="project-board" aria-labelledby="project-board-title">
        <div className="section-heading board-heading">
          <div>
            <p className="eyebrow">PROJECT BOARD</p>
            <h2 id="project-board-title">项目灵感与分析记录</h2>
          </div>
          <button className="refresh-button" type="button" onClick={loadProjects} disabled={isLoading}>
            <RefreshIcon />
            {isLoading ? '同步中' : '刷新'}
          </button>
        </div>

        <div className="filter-row" aria-label="项目类型筛选">
          {SERVICE_PRESENTATIONS.slice(0, 9).map((service) => (
            <button
              className={activeService === service.value ? 'filter-chip active' : 'filter-chip'}
              type="button"
              key={service.value}
              onClick={() => setActiveService(service.value)}
            >
              {service.shortLabel}
            </button>
          ))}
        </div>

        {isLoading && projects.length === 0 ? (
          <div className="project-skeletons" aria-label="正在加载项目">
            {[1, 2, 3, 4].map((item) => <span key={item} />)}
          </div>
        ) : null}

        {!isLoading && visibleProjects.length === 0 ? (
          <div className="empty-board">
            <span aria-hidden="true">✦</span>
            <h3>{projects.length === 0 ? '还没有项目，先创建第一份分析' : '没有匹配的项目'}</h3>
            <p>{projects.length === 0 ? '点击“填入示例”可以在一分钟内跑通完整流程。' : '尝试清空搜索或切换服务类型。'}</p>
          </div>
        ) : (
          <div className="masonry-board">
            {visibleProjects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                isSelected={selectedProject?.id === project.id}
                onSelect={setSelectedProject}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

function toMessage(error: unknown): string {
  if (error instanceof HttpError) return error.message
  if (error instanceof TypeError) return '无法连接后端，请确认 FastAPI 已在 8000 端口启动。'
  return '操作失败，请稍后重试。'
}
