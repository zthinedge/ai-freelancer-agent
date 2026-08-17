# 接单智策：AI Native Agent架构与学习路线

## 1. 这份文档解决什么问题

本项目不仅要“内置AI”，还要用一个真实业务场景掌握企业开发Agent时常见的工程能力。本学习路线围绕接单智策逐步增加能力，每个知识点都必须在产品中有可演示、可测试的落点。

产品目标与学习目标需要分开：

- 产品目标：帮助自由职业者澄清需求、控制范围、估算工时和准备报价；
- 学习目标：掌握Agent、Workflow、Skill、Tool、State、Guardrail、Trace和Eval；
- 判断标准：用户不需要理解Agent术语，也能完成接单分析；开发者可以通过步骤面板、代码和评测说明Agent如何工作。

## 2. 先建立正确的概念地图

### 2.1 LLM应用、Workflow与Agent

| 类型 | 谁决定下一步 | 适用情况 | 本项目示例 |
|---|---|---|---|
| 单次LLM调用 | 程序只请求一次模型 | 文本改写、摘要 | 把方案改写为客户语气 |
| Workflow | 代码预先规定步骤和分支 | 流程稳定、风险可控 | 先澄清，再拆任务，最后报价 |
| Agent | 模型根据目标和状态选择下一步与Tool | 输入开放、路径无法完全预设 | 判断缺少哪些信息、该调用哪个Skill |

Agent并不等于多Agent。一个拥有目标、状态、工具和循环能力的主Agent，已经能够展示完整的Agent系统；多个Agent只有在需要独立专业上下文、权限或并行工作时才值得引入。

### 2.2 Skill、Tool与MCP的区别

| 概念 | 本质 | 接单智策中的例子 |
|---|---|---|
| Skill | 可复用的专业做事方法，包含指令、契约、资料和测试 | `scope_designer`规定如何划分Must／Should／Could／Won't |
| Tool | 可执行且结果相对确定的函数或服务 | `pricing_calculator`根据参数计算金额 |
| MCP | 让Agent用统一协议发现外部资源、Prompt和Tool的连接层 | 后续读取企业报价规则库或项目管理系统 |

简单记忆：Skill告诉Agent“这类事应该怎么做”，Tool让Agent“真的执行一个动作”，MCP让外部系统“以标准方式把能力提供给Agent”。

## 3. 企业通常需要的Agent能力

### 3.1 模型与提示工程

- 清楚区分系统指令、业务上下文、用户数据和参考资料；
- 使用结构化输出Schema，而不是依赖不稳定的自然语言格式；
- 管理Prompt版本、少样本示例、Token预算、延迟和成本；
- 根据任务选择模型，不把所有步骤都交给最高成本模型。

项目落点：六个Skill均使用固定输入输出契约，并记录Prompt／Skill版本。

### 3.2 Tool Calling与API集成

- 设计清晰的Tool名称、描述、参数Schema和错误码；
- 处理超时、重试、限流、幂等和部分失败；
- 区分只读与写操作，执行最小权限和人工审批；
- 理解MCP的Host、Client、Server以及Resources、Prompts、Tools。

项目落点：先实现本地报价Tool和项目查询Tool，再在后续版本接入一个只读MCP数据源。

### 3.3 工作流与编排

需要掌握的常见模式：

1. Prompt Chaining：上一步结构化结果成为下一步输入；
2. Routing：根据项目类型选择开发、设计或内容规则；
3. Parallelization：范围已确认后，可并行检查技术风险和商务风险；
4. Orchestrator-Workers：主Agent把独立子任务分配给专业执行者；
5. Evaluator-Optimizer：评审器按标准检查草案，不合格时限次修改；
6. Human-in-the-loop：在高风险决策前暂停、审批并恢复；
7. Fallback：模型不可用或输出不合格时降级为规则模板。

项目落点：MVP使用Prompt Chaining、Routing、Human-in-the-loop和Fallback；并行与评审器放到v0.3。

### 3.4 状态、记忆与可靠性

- 区分当前运行状态、会话记忆、用户偏好和长期业务知识；
- 用Checkpoint保存节点状态，使流程可暂停、恢复和重放；
- 防止同一请求重复扣费、重复创建项目或重复发送；
- 对失败进行分类，明确哪些可重试、哪些必须人工处理。

项目落点：`AgentRun`保存当前节点和结构化状态，用户回答澄清问题后从指定节点继续运行。

### 3.5 RAG与企业数据

- 数据清洗、分块、检索、重排、引用和权限过滤；
- 明确“模型记忆”与“检索企业知识”的差异；
- 确保不同用户只能检索其有权限访问的数据；
- 对来源、版本和更新时间进行记录。

项目落点：MVP不做向量数据库；v0.3可加入“小型历史报价案例库”，只有验证历史案例确实改善结果后再升级为RAG。

### 3.6 安全、Guardrail与治理

- 防Prompt Injection、数据泄露、越权Tool调用和不安全输出；
- 对输入、Tool参数、Tool结果和最终输出分别校验；
- 敏感数据脱敏，密钥只保存在服务端；
- 高风险操作保留人工审批和审计记录。

项目落点：客户原话始终按不可信数据处理；报价、对外发送和外部写操作必须人工确认。

### 3.7 Eval、Trace与可观测性

- 建立固定案例集和预期标准，修改Prompt后自动回归；
- 同时评测最终结果与过程：是否选对Skill、参数是否正确、是否越过人工节点；
- 记录模型调用、Tool调用、耗时、Token、成本、错误和降级；
- 用线上用户反馈补充离线评测，但不把“看起来不错”当作唯一标准。

项目落点：准备10个固定接单案例，评测完整性、追问有效性、范围边界、报价公式和风险发现。

### 3.8 软件工程与产品能力

- Python／TypeScript、API设计、数据库、异步任务、测试、Git和CI/CD；
- 业务建模、需求优先级、用户访谈、成本收益和验收指标；
- 能解释为什么这里需要Agent，为什么另一些步骤必须使用确定性代码。

企业需要的不是“会写一个神奇Prompt”，而是能够把不稳定模型放进可控制、可测试、可维护的业务系统。

## 4. 接单智策的目标架构

```text
Web界面
  -> Agent API
      -> 输入Guardrail
      -> Workflow / State Machine
          -> 接单策略Agent
              -> Skill Registry
                  -> requirement_intake
                  -> clarification_planner
                  -> scope_designer
                  -> task_estimator
                  -> risk_reviewer
                  -> proposal_writer
              -> Tool Registry
                  -> pricing_calculator
                  -> project_store
          -> Checkpoint / Human Approval
      -> 输出Guardrail
      -> Trace / Eval / Cost Metrics
  -> SQLite（MVP）
```

### 为什么选“主Agent + Skill”，而不是六个Agent

- 六个步骤共享大量上下文，拆成多个Agent会重复传输Token；
- 第一版更需要可控、稳定和易调试，而不是最大自治；
- Skill可以独立测试，后续也能无痛升级为专家Agent；
- 主Agent保留统一的用户体验和最终结果责任。

满足以下任一条件时，再把Skill升级为Agent：

- 需要独立的长上下文或知识库；
- 需要与其他步骤不同的模型、权限或安全规则；
- 可与其他工作并行且能明显降低总耗时；
- 需要多轮自主执行和独立质量评测。

## 5. Skill的标准结构

实现阶段，每个Skill至少包含如下信息：

```yaml
name: scope_designer
version: 0.1.0
description: 将已确认需求拆分为MoSCoW范围并明确排除项
triggers:
  - 关键信息已完成用户确认
do_not_use_when:
  - 交付物或目标仍未知
inputs:
  - confirmed_facts
  - clarification_answers
outputs:
  - must
  - should
  - could
  - wont
allowed_tools: []
guardrails:
  - must至少2项
  - wont至少2项
  - 不虚构用户未提供的约束
evaluation_cases:
  - cases/scope_web_mvp.json
  - cases/scope_ai_chat.json
  - cases/scope_urgent_ppt.json
```

Skill编排必须遵守以下规则：

1. 由触发条件和当前状态决定是否执行，而不是把所有Skill无条件塞入Prompt；
2. Skill只获得完成任务所需的最小上下文；
3. Skill输出必须通过Schema和业务规则校验；
4. 同一Skill自动修复最多一次，仍失败则降级或人工处理；
5. 每次执行记录Skill名称、版本、输入摘要、结果、耗时和错误；
6. 新Skill必须先通过离线案例，再加入主工作流。

## 6. 分阶段学习与开发路线

### 阶段0：需求与评测先行（当前阶段）

目标：先定义Agent为什么存在，以及什么叫“做对了”。

产物：PRD、状态图、Skill清单、10个评测案例、验收指标。

### 阶段1：结构化LLM应用

学习：Prompt分层、结构化输出、模型API、错误处理、成本统计。

产品产物：`requirement_intake`和`clarification_planner`，输入客户原话后得到稳定JSON。

### 阶段2：Workflow与Tool

学习：Prompt Chaining、Routing、函数调用、确定性计算、重试与降级。

产品产物：六步流程和`pricing_calculator`，形成从需求到报价的闭环。

### 阶段3：真正的Agent循环

学习：Agent根据状态选择Skill、Tool Calling、停止条件、Token／步数上限。

产品产物：接单策略Agent只调用完成当前任务所需的Skill，并能解释操作依据。

### 阶段4：状态与Human-in-the-loop

学习：Checkpoint、暂停恢复、幂等、审批和审计。

产品产物：用户补充澄清答案后继续运行；报价确认后才能标记为最终方案。

### 阶段5：Eval与Observability

学习：案例集、过程评测、Trace、延迟、Token、成本和线上反馈。

产品产物：10个案例回归报告和Agent步骤面板，能对比Skill版本变化。

### 阶段6：MCP与多Agent（扩展）

学习：MCP能力发现、权限边界、Manager与Handoff、并行任务和上下文隔离。

产品产物：先接入一个只读外部数据源；再将`risk_reviewer`升级为独立评审Agent，并用评测证明复杂度增加是值得的。

## 7. 课程MVP的合理边界

第一周必须完成：

- 一个面向用户的主Agent；
- 六个可独立说明的Skill，其中至少四个进入演示主流程；
- 一个确定性报价Tool；
- 两个人工确认节点；
- 结构化状态与运行记录；
- 10个固定案例的基础评测；
- 一次完整演示：模糊需求 → 追问 → 补充 → 范围 → 工时 → 报价 → 确认。

第一周不要求：

- 多Agent自治团队；
- 向量数据库和复杂RAG；
- 自建MCP Server；
- 长期自主运行、自动联系客户或自动成交；
- 生产级账号、支付和团队权限。

## 8. 最终作品可以证明什么

完成上述路线后，作品集不只是“做了一个AI报价页面”，而是可以具体证明：

- 能识别适合Agent与适合确定性代码的边界；
- 能设计状态化Workflow与Human-in-the-loop；
- 能把业务能力封装为可复用、可评测的Skill；
- 能设计安全的Tool并理解MCP扩展方式；
- 能用Trace和Eval定位Agent问题，而不是只反复调Prompt；
- 能兼顾产品价值、成本、稳定性、安全和工程交付。

## 9. 官方参考资料

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [OpenAI Agent orchestration](https://openai.github.io/openai-agents-python/multi_agent/)
- [OpenAI Guardrails](https://openai.github.io/openai-agents-python/guardrails/)
- [OpenAI Tracing](https://openai.github.io/openai-agents-python/tracing/)
- [Anthropic：Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Claude Platform：Agent Skills](https://platform.claude.com/docs/en/managed-agents/skills)
- [Model Context Protocol Architecture](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
