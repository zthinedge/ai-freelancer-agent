import { useEffect, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'

import type { ProjectAnalysis } from '../../../entities/project-analysis/model/projectAnalysis'
import { getServicePresentation } from '../../../entities/project/model/serviceType'
import { ArrowIcon, CloseIcon, SparklesIcon } from '../../../shared/ui/Icons'

type AnalysisPanelProps = Readonly<{
  project: ProjectAnalysis | null
  isSubmitting: boolean
  onSubmitAnswers: (answers: Readonly<Record<string, string>>) => Promise<void>
  onClose: () => void
  quoteContent: ReactNode
}>

const statusLabels = {
  pending: '等待开始',
  running: '分析中',
  waiting_user: '等待补充',
  waiting_approval: '等待确认',
  completed: '澄清完成',
  failed: '运行失败',
} as const

export function AnalysisPanel({
  project,
  isSubmitting,
  onSubmitAnswers,
  onClose,
  quoteContent,
}: AnalysisPanelProps) {
  const runId = project?.run?.id ?? null
  const questions = project?.run?.state.pendingQuestions ?? []
  const [answersByQuestionId, setAnswersByQuestionId] = useState<Record<string, string>>({})
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setAnswersByQuestionId({})
    setError(null)
  }, [runId])

  if (project === null || project.run === null) {
    return (
      <aside className="analysis-panel empty" aria-label="Agent分析结果">
        <span className="empty-orbit" aria-hidden="true">
          <SparklesIcon />
        </span>
        <p className="eyebrow">AGENT WORKSPACE</p>
        <h2>分析结果会出现在这里</h2>
        <p>创建项目后，后端会返回已知事实、缺失字段和最值得先问客户的问题。</p>
        <ol className="mini-flow">
          <li><span>1</span>提取事实</li>
          <li><span>2</span>发现缺口</li>
          <li><span>3</span>等待人工补充</li>
        </ol>
      </aside>
    )
  }

  const { run } = project
  const service = getServicePresentation(project.serviceType)
  const completed = run.status === 'completed'
  const failed = run.status === 'failed'
  const hasQuote = run.state.pricing !== null && run.state.proposal !== null
  const engineLabel =
    run.state.executionMode === 'model'
      ? run.state.modelName ?? 'AI 模型'
      : run.state.fallbackReason === null
        ? '规则模式'
        : '模型降级 · 规则模式'
  const engineDetails =
    run.state.executionMode === 'model'
      ? [
          run.state.modelName,
          run.state.fallbackReason,
          run.state.modelInputTokens === null ? null : `输入 ${run.state.modelInputTokens} tokens`,
          run.state.modelOutputTokens === null ? null : `输出 ${run.state.modelOutputTokens} tokens`,
          run.state.modelLatencyMs === null ? null : `耗时 ${run.state.modelLatencyMs} ms`,
        ]
          .filter(Boolean)
          .join(' · ')
      : run.state.fallbackReason ?? '当前项目使用本地规则模式，不调用外部模型'

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const unanswered = questions.find(
      (question) => !answersByQuestionId[question.questionId]?.trim(),
    )
    if (unanswered) {
      setError(`请先回答：${unanswered.question}`)
      return
    }
    setError(null)
    const answers = Object.fromEntries(
      questions.map((question) => [
        question.questionId,
        answersByQuestionId[question.questionId]?.trim() ?? '',
      ]),
    )
    await onSubmitAnswers(answers)
  }

  return (
    <aside className="analysis-panel populated" aria-live="polite">
      <div className={`analysis-cover tone-${service.tone}`}>
        <div>
          <span className="service-symbol">{service.symbol}</span>
          <p>{service.label}</p>
          <h2>{project.name}</h2>
        </div>
        <button className="icon-button" type="button" onClick={onClose} aria-label="关闭分析面板">
          <CloseIcon />
        </button>
        <span className="cover-shape one" />
        <span className="cover-shape two" />
      </div>

      <div className="analysis-body">
        <div className="run-heading">
          <div>
            <p className="eyebrow">LIVE AGENT RUN</p>
            <h3>
              {completed
                ? '方案与报价已确认'
                : failed
                  ? '自动分析已安全停止'
                : hasQuote
                  ? '请选择方案并人工确认报价'
                  : 'Agent 需要你确认这些信息'}
            </h3>
          </div>
          <div className="run-badges">
            <span className={`engine-badge ${run.state.executionMode}`} title={engineDetails}>
              {engineLabel}
            </span>
            <span className={`run-status ${run.status}`}>{statusLabels[run.status]}</span>
          </div>
        </div>

        <div className="step-track" aria-label="Agent执行步骤">
          <span className="done">需求提取</span>
          <i />
          <span className={run.state.clarificationApproved ? 'done' : 'active'}>澄清问题</span>
          <i />
          <span className={run.state.pricing ? (completed ? 'done' : 'active') : ''}>范围与报价</span>
        </div>

        <section className="facts-block">
          <div className="block-title">
            <h4>已确认事实</h4>
            <span>{run.state.confirmedFacts.length} 项</span>
          </div>
          <div className="fact-pills">
            {run.state.confirmedFacts.map((fact, index) => (
              <span key={`${fact.field}-${index}`} title={fact.evidence}>
                <small>{fact.field}</small>
                {fact.value}
              </span>
            ))}
          </div>
        </section>

        {run.state.retrievedContext.length > 0 ? (
          <section className="facts-block" aria-label="RAG检索记忆">
            <div className="block-title">
              <h4>RAG参考记忆</h4>
              <span>{run.state.retrievedContext.length} 条</span>
            </div>
            <div className="fact-pills">
              {run.state.retrievedContext.map((item, index) => (
                <span key={`${item.sourceId}-${index}`} title={item.excerpt}>
                  <small>相关度 {Math.round(item.score * 100)}%</small>
                  {item.title}
                </span>
              ))}
            </div>
          </section>
        ) : null}

        {run.state.pricing && run.state.proposal ? (
          quoteContent
        ) : completed ? (
          <div className="completion-card">
            <span aria-hidden="true">✓</span>
            <div>
              <h4>信息已合并到项目状态</h4>
              <p>下一阶段会继续生成范围、工时、风险和报价方案。</p>
            </div>
          </div>
        ) : failed ? (
          <div className="completion-card" role="alert">
            <span aria-hidden="true">!</span>
            <div>
              <h4>自动分析已安全停止</h4>
              <p>{run.state.fallbackReason ?? '模型未能生成可靠结果，当前不会产生可批准报价。'}</p>
            </div>
          </div>
        ) : (
          <form className="questions-form" onSubmit={handleSubmit}>
            <div className="block-title">
              <h4>高价值澄清问题</h4>
              <span>{questions.length} 题</span>
            </div>
            {questions.map((question, index) => (
              <label className="question-item" key={question.questionId}>
                <span className="question-number">{String(index + 1).padStart(2, '0')}</span>
                <span className="question-content">
                  <strong>{question.question}</strong>
                  <small>{question.reason}</small>
                  <input
                    value={answersByQuestionId[question.questionId] ?? ''}
                    onChange={(event) =>
                      setAnswersByQuestionId((current) => ({
                        ...current,
                        [question.questionId]: event.target.value,
                      }))
                    }
                    placeholder="输入客户回答或你的确认结果"
                  />
                </span>
              </label>
            ))}
            {error ? <p className="form-error">{error}</p> : null}
            <button className="secondary-action" type="submit" disabled={isSubmitting}>
              <span>{isSubmitting ? '正在保存…' : '保存回答并继续'}</span>
              {isSubmitting ? <i className="spinner dark" /> : <ArrowIcon />}
            </button>
          </form>
        )}
      </div>
    </aside>
  )
}
