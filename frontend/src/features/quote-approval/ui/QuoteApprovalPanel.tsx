import { useState } from 'react'

import type {
  AgentState,
  QuoteTier,
} from '../../../entities/agent-run/model/agentContracts'
import { ArrowIcon } from '../../../shared/ui/Icons'

type QuoteApprovalPanelProps = Readonly<{
  state: AgentState
  isSubmitting: boolean
  onApprove: (selectedTier: QuoteTier, note: string | null) => Promise<void>
}>

const TIER_COPY: Record<QuoteTier, Readonly<{ label: string; caption: string }>> = {
  basic: { label: '乐观估算', caption: '相同范围，按顺利条件下界估算' },
  standard: { label: '推荐估算', caption: '相同范围，按期望工时与风险估算' },
  premium: { label: '保守估算', caption: '相同范围，按工时上界与保障估算' },
}

const PRICE_FORMATTER = new Intl.NumberFormat('zh-CN', {
  style: 'currency',
  currency: 'CNY',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

export function QuoteApprovalPanel({
  state,
  isSubmitting,
  onApprove,
}: QuoteApprovalPanelProps) {
  const [selectedTier, setSelectedTier] = useState<QuoteTier>(
    state.selectedQuoteTier ?? 'standard',
  )
  const [note, setNote] = useState('')
  const { pricing, proposal, estimate, riskReview } = state

  if (pricing === null || proposal === null || estimate === null || riskReview === null) {
    return null
  }

  const selected = pricing.options.find((option) => option.tier === selectedTier) ?? pricing.options[1]
  const totalMinHours = estimate.tasks.reduce((total, task) => total + Number(task.minHours), 0)
  const taskMaxHours = estimate.tasks.reduce((total, task) => total + Number(task.maxHours), 0)
  const totalMaxHours = taskMaxHours + Number(estimate.bufferHours)

  return (
    <section className="quote-workspace" aria-labelledby="quote-title">
      <div className="quote-hero">
        <div>
          <p className="eyebrow">AI QUOTE DRAFT</p>
          <h4 id="quote-title">范围、工时与三级报价已生成</h4>
          <p>{proposal.projectSummary}</p>
        </div>
        <div className="hours-summary" aria-label="工时估算">
          <strong>{totalMinHours}–{totalMaxHours}</strong>
          <span>预计工时（含 {estimate.bufferHours}h 缓冲）</span>
        </div>
      </div>

      <div className="quote-options" role="radiogroup" aria-label="选择报价方案">
        {pricing.options.map((option) => {
          const copy = TIER_COPY[option.tier]
          const active = selectedTier === option.tier
          return (
            <button
              key={option.tier}
              className={active ? 'quote-option active' : 'quote-option'}
              type="button"
              role="radio"
              aria-checked={active}
              onClick={() => setSelectedTier(option.tier)}
            >
              {option.tier === 'standard' ? <small className="recommended-tag">推荐</small> : null}
              <span>{copy.label}</span>
              <strong>{PRICE_FORMATTER.format(Number(option.amount.amount))}</strong>
              <small>{copy.caption}</small>
              <em>{option.includedHours} 小时</em>
            </button>
          )
        })}
      </div>

      <div className="quote-columns">
        <section>
          <div className="block-title">
            <h4>交付范围</h4>
            <span>{proposal.deliverables.length} 项</span>
          </div>
          <ul className="detail-list positive">
            {proposal.deliverables.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        </section>
        <section>
          <div className="block-title">
            <h4>明确不包含</h4>
            <span>{proposal.exclusions.length} 项</span>
          </div>
          <ul className="detail-list muted">
            {proposal.exclusions.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        </section>
      </div>

      <details className="quote-details">
        <summary>查看计算依据、任务拆解与风险</summary>
        <p className="calculation-note">{selected.calculationSummary}</p>
        <ol className="task-list">
          {estimate.tasks.map((task) => (
            <li key={task.taskId}>
              <span><strong>{task.title}</strong><small>{task.description}</small></span>
              <b>{task.minHours}–{task.maxHours}h</b>
            </li>
          ))}
        </ol>
        {riskReview.risks.map((risk) => (
          <p className={`risk-note ${risk.severity}`} key={risk.riskId}>
            <strong>{risk.severity === 'high' ? '高风险' : '需注意'}：</strong>
            {risk.cause}；{risk.mitigation}
          </p>
        ))}
      </details>

      {state.quoteApproved ? (
        <div className="completion-card quote-approved" role="status">
          <span aria-hidden="true">✓</span>
          <div>
            <h4>{TIER_COPY[state.selectedQuoteTier ?? selectedTier].label}报价已确认</h4>
            <p>该版本已通过人工节点，可以作为后续沟通和方案整理的依据。</p>
          </div>
        </div>
      ) : (
        <div className="quote-approval-box">
          <label htmlFor="quote-note">确认备注（可选）</label>
          <textarea
            id="quote-note"
            value={note}
            onChange={(event) => setNote(event.target.value)}
            placeholder="例如：客户倾向标准版，最终金额需在素材确认后锁定"
            maxLength={500}
          />
          <button
            className="secondary-action"
            type="button"
            disabled={isSubmitting}
            onClick={() => onApprove(selectedTier, note.trim() || null)}
          >
            <span>
              {isSubmitting ? '正在确认报价…' : `确认${TIER_COPY[selectedTier].label}报价`}
            </span>
            {isSubmitting ? <i className="spinner dark" /> : <ArrowIcon />}
          </button>
          <small className="approval-warning">
            确认前仅为AI草案，不会自动发送给客户，也不会自动成交。
          </small>
        </div>
      )}

      <div className="quote-disclaimers">
        {proposal.disclaimers.map((item, index) => <p key={`${item}-${index}`}>※ {item}</p>)}
      </div>
    </section>
  )
}
