const layers = [
  {
    label: 'APP / PAGES',
    title: '应用装配与页面编排',
    description: '只负责路由、全局Provider和页面组合，不保存具体业务规则。',
  },
  {
    label: 'FEATURES',
    title: '用户动作',
    description: '项目录入、查看Agent运行、提交澄清答案和确认报价彼此独立。',
  },
  {
    label: 'ENTITIES',
    title: '稳定业务模型',
    description: 'Project、AgentRun与SkillExecution类型不依赖React组件或HTTP实现。',
  },
  {
    label: 'SHARED',
    title: '无业务含义的基础能力',
    description: 'HTTP契约、运行配置和通用UI向上提供能力，不反向引用Feature。',
  },
] as const


export function ArchitecturePage() {
  return (
    <div className="page">
      <section className="hero">
        <p className="eyebrow">ARCHITECTURE BASELINE · V0.2</p>
        <h1>先建立稳定边界，再实现Agent能力。</h1>
        <p>
          当前版本只验证前后端骨架、模块边界和扩展点。项目分析、Skill执行与报价逻辑将在后续阶段按用例逐步接入。
        </p>
      </section>

      <section className="layer-grid" aria-label="前端架构分层">
        {layers.map((layer) => (
          <article className="layer-card" key={layer.label}>
            <span>{layer.label}</span>
            <h2>{layer.title}</h2>
            <p>{layer.description}</p>
          </article>
        ))}
      </section>

      <section className="flow-card">
        <p className="eyebrow">DEPENDENCY DIRECTION</p>
        <h2>依赖只能向稳定内层流动</h2>
        <p className="flow">app → pages → features → entities → shared</p>
      </section>
    </div>
  )
}
