import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'

import { SERVICE_PRESENTATIONS } from '../../../entities/project/model/serviceType'
import type { ServiceType } from '../../../entities/project/model/project'
import { ArrowIcon, SparklesIcon } from '../../../shared/ui/Icons'
import type { ProjectIntakeDraft } from '../model/contracts'

type ProjectComposerProps = Readonly<{
  focusSignal: number
  isSubmitting: boolean
  onSubmit: (draft: ProjectIntakeDraft) => Promise<void>
}>

const EXAMPLE_REQUEST =
  '我们要重做公司官网，中英文双语，包含首页、产品、案例、关于我们和联系页面，要求手机端适配，希望三周上线。'

export function ProjectComposer({ focusSignal, isSubmitting, onSubmit }: ProjectComposerProps) {
  const sectionRef = useRef<HTMLElement>(null)
  const nameRef = useRef<HTMLInputElement>(null)
  const [name, setName] = useState('')
  const [clientRequest, setClientRequest] = useState('')
  const [serviceType, setServiceType] = useState<ServiceType>('auto_detect')
  const [budget, setBudget] = useState('')
  const [deadline, setDeadline] = useState('')
  const [hourlyRate, setHourlyRate] = useState('150')
  const [validationError, setValidationError] = useState<string | null>(null)

  useEffect(() => {
    if (focusSignal === 0) return
    sectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    window.setTimeout(() => nameRef.current?.focus(), 350)
  }, [focusSignal])

  const fillExample = () => {
    setName('制造企业官网改版')
    setClientRequest(EXAMPLE_REQUEST)
    setServiceType('website')
    setBudget('12000')
    setDeadline('三周内')
    setValidationError(null)
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (name.trim().length < 2) {
      setValidationError('项目名称至少需要 2 个字。')
      nameRef.current?.focus()
      return
    }
    if (clientRequest.trim().length < 10) {
      setValidationError('请至少用 10 个字描述客户需求。')
      return
    }
    if (!hourlyRate || Number(hourlyRate) <= 0) {
      setValidationError('请填写大于 0 的接单时薪。')
      return
    }

    setValidationError(null)
    await onSubmit({
      schemaVersion: '1.0.0',
      name: name.trim(),
      clientRequest: clientRequest.trim(),
      serviceType,
      budget: budget ? { amount: Number(budget).toFixed(2), currency: 'CNY' } : null,
      deadline: deadline.trim() || null,
      hourlyRate: { amount: Number(hourlyRate).toFixed(2), currency: 'CNY' },
    })
  }

  return (
    <section className="composer-card" id="new-analysis" ref={sectionRef} aria-labelledby="composer-title">
      <div className="section-heading compact">
        <div>
          <p className="eyebrow">NEW ANALYSIS</p>
          <h2 id="composer-title">把客户原话交给 Agent</h2>
        </div>
        <button className="text-button" type="button" onClick={fillExample}>
          填入示例
        </button>
      </div>

      <form onSubmit={handleSubmit} noValidate>
        <label className="field-label" htmlFor="project-name">
          项目名称
        </label>
        <input
          ref={nameRef}
          id="project-name"
          className="text-input"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="例如：品牌官网改版"
          maxLength={100}
        />

        <div className="field-row-label">
          <span className="field-label">服务类型</span>
          <small>帮助 Agent 选择更相关的问题</small>
        </div>
        <div className="service-picker" role="radiogroup" aria-label="服务类型">
          {SERVICE_PRESENTATIONS.slice(0, 9).map((service) => (
            <button
              className={serviceType === service.value ? 'service-chip active' : 'service-chip'}
              key={service.value}
              type="button"
              role="radio"
              aria-checked={serviceType === service.value}
              onClick={() => setServiceType(service.value)}
            >
              <span>{service.symbol}</span>
              {service.shortLabel}
            </button>
          ))}
        </div>

        <label className="field-label" htmlFor="client-request">
          客户原话
        </label>
        <textarea
          id="client-request"
          className="request-input"
          value={clientRequest}
          onChange={(event) => setClientRequest(event.target.value)}
          placeholder="粘贴聊天中的原始需求。不要替客户补充没有说过的信息……"
          maxLength={5000}
        />
        <div className="input-meta">
          <span>客户文本仅作为数据处理，不会覆盖系统规则</span>
          <span>{clientRequest.length}/5000</span>
        </div>

        <div className="three-fields">
          <label>
            <span className="field-label">预算（可选）</span>
            <span className="input-with-prefix">
              <b>¥</b>
              <input
                type="number"
                min="0"
                step="100"
                value={budget}
                onChange={(event) => setBudget(event.target.value)}
                placeholder="12000"
              />
            </span>
          </label>
          <label>
            <span className="field-label">期望期限</span>
            <input
              className="text-input"
              value={deadline}
              onChange={(event) => setDeadline(event.target.value)}
              placeholder="例如：三周内"
              maxLength={80}
            />
          </label>
          <label>
            <span className="field-label">我的时薪</span>
            <span className="input-with-prefix">
              <b>¥</b>
              <input
                type="number"
                min="1"
                step="10"
                value={hourlyRate}
                onChange={(event) => setHourlyRate(event.target.value)}
              />
            </span>
          </label>
        </div>

        {validationError ? <p className="form-error">{validationError}</p> : null}

        <button className="primary-action" type="submit" disabled={isSubmitting}>
          <SparklesIcon />
          <span>{isSubmitting ? 'Agent 正在梳理需求…' : '开始需求分析'}</span>
          {isSubmitting ? <i className="spinner" aria-hidden="true" /> : <ArrowIcon />}
        </button>
      </form>
    </section>
  )
}
