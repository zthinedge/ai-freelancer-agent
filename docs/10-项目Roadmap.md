# 接单智策项目 Roadmap

版本：v1.0
更新日期：2026-08-19
当前基线：`v0.3 Intake & Clarification MVP`
当前提交：`0816ad0 feat: complete intake and clarification workflow`

## 1. Roadmap目标

这份Roadmap用于回答三个问题：

1. 当前项目已经完成到哪里；
2. 下一步应该按什么顺序开发；
3. 每个阶段达到什么结果才算完成。

课程MVP坚持“先闭环、再增强”的原则。范围、报价、人工确认、评测和部署完成前，不提前加入复杂RAG、多Agent自治、自动联系客户或支付合同能力。

## 2. 当前所处位置

```mermaid
flowchart LR
    A[需求与架构<br/>P0-P1 ✅] --> B[评测与契约<br/>P2 ✅]
    B --> C[需求提取与澄清<br/>P3-P4 ✅]
    C --> D[真实模型与完整方案<br/>P5 下一步]
    D --> E[持久化与人工审批<br/>P6]
    E --> F[评测、安全与用户验证<br/>P7]
    F --> G[部署与作业材料<br/>P8]
```

当前系统已经能够完成：

- 前端创建项目并调用后端API；
- 规则回退Agent提取已知事实并生成3-6个澄清问题；
- 用户提交答案后恢复工作流并完成澄清阶段；
- 搜索、筛选、项目卡片、Agent状态和响应式页面交互；
- 10个固定评测案例与严格的前后端数据契约；
- 后端19项自动化测试、前端生产构建和浏览器联调验收。

当前主要限制：

- 尚未接入真实大模型，当前由确定性规则回退执行需求提取；
- 只完成需求提取和澄清，没有生成范围、工时、风险、报价和方案；
- 使用内存存储，后端重启后项目数据会清空；
- 尚未形成最终评测报告、用户测试、在线部署和课程提交材料。

## 3. 总体里程碑

| 里程碑 | 对应阶段 | 核心目标 | 主要交付物 | 预计投入 | 状态 |
|---|---|---|---|---:|---|
| M0 基础闭环 | P0-P4 | 从客户原话走到澄清完成 | PRD、架构、Eval、API、响应式工作台 | 已完成 | ✅ |
| M1 AI方案生成 | P5 | 接入真实模型并生成可复算的接单方案 | Model Gateway、6个Skill、报价Tool、方案页 | 1-1.5天 | 🟡 M1-A完成，下一步M1-B |
| M2 状态与审批 | P6 | 数据可恢复，关键结论必须由人确认 | SQLite、Checkpoint、幂等、范围与报价审批 | 0.5-1天 | ⬜ |
| M3 质量验证 | P7 | 用数据证明Agent稳定、安全、有帮助 | Eval Runner、Trace、测试报告、3名用户反馈 | 0.5-1天 | ⬜ |
| M4 发布交付 | P8 | 项目可在线演示并满足课程提交要求 | 部署链接、README、PPT、截图、演示视频 | 0.5-1天 | ⬜ |

剩余课程MVP预计需要3-4个有效开发日。如果时间不足，优先保证M1、M2的主链路和M4的可演示性，复杂优化放入后续版本。

## 4. M1：真实模型与完整方案生成

### M1-A 模型网关与前两个Skill

当前状态：模型网关、Prompt、结构化校验、自动Fallback和前端模式展示已实现；DeepSeek V4 Flash线上Smoke Test与前端完整澄清流程均已通过。

目标：在不破坏现有规则回退的前提下，让需求提取和澄清真正调用大模型。

任务：

- 实现OpenAI兼容的`ModelGateway`基础设施适配器；
- 从环境变量读取模型地址、模型名、API Key、超时和重试配置；
- 禁止在代码、日志和Git提交中保存API Key；
- 将`requirement_intake`和`clarification_planner`改为结构化模型输出；
- 使用现有Pydantic Schema校验模型结果，校验失败时重试或降级；
- 保留`RuleBasedIntakeAgent`作为无密钥、本地测试和模型故障时的Fallback；
- 记录模型名称、Prompt版本、耗时、Token和失败原因。

验收标准：

- 没有API Key时仍可通过规则回退跑完整个现有流程；
- 配置API Key后，两项Skill可返回符合Schema的数据；
- 模型超时、非JSON、字段缺失和越权指令不会导致服务崩溃；
- `eval-010-prompt-injection.json`中的攻击文本不会覆盖系统规则；
- 相关单元测试和API测试通过。

### M1-B 剩余Skill编排

目标：把澄清完成后的项目转成可确认、可复算的接单方案。

执行顺序：

```text
requirement_intake
→ clarification_planner
→ 人工补充信息
→ scope_designer
→ task_estimator
→ risk_reviewer
→ pricing_calculator Tool
→ proposal_writer
→ 人工确认
```

任务：

- `scope_designer`：输出Must、Should、Could和Out of Scope；
- `task_estimator`：输出任务、乐观／常规／悲观工时和估算依据；
- `risk_reviewer`：输出风险等级、影响、概率、应对措施和报价建议；
- `pricing_calculator`：用确定性代码计算基础价、风险缓冲、加急费和总价；
- `proposal_writer`：生成基础、标准和高级三档客户方案；
- 前端增加范围、工时、风险、报价和方案展示区；
- 所有Skill沿用`schema_version`、`prompt_version`和`run_id`追踪规则。

验收标准：

- 从客户原话到三档方案可以完整运行；
- 所有Skill输出通过Pydantic Schema校验；
- 相同输入和费率的报价可以由程序100%复算；
- 模型只能提出价格建议，最终金额由报价Tool计算；
- 未回答关键澄清问题时，不允许跳过人工节点直接生成最终报价。

## 5. M2：持久化、Checkpoint与人工审批

目标：让项目从演示原型升级为可恢复、可审计的工作流。

任务：

- 用SQLite实现`ProjectRepository`、`AgentRunRepository`和`SkillExecutionRepository`；
- 保存项目、Agent状态、每次Skill输入输出、Prompt版本和执行时间；
- 在澄清、范围和报价节点保存Checkpoint；
- 增加范围确认、报价确认和拒绝修改接口；
- 对提交答案和确认操作增加幂等键，避免重复执行；
- 前端刷新后恢复当前项目和Agent步骤；
- 保留内存适配器供测试使用。

验收标准：

- 重启前后端后，历史项目和运行状态仍然存在；
- 同一份答案重复提交不会生成两次结果；
- 未确认范围不能进入最终报价；
- 未确认报价不能标记为最终客户方案；
- 可以查看每个Skill的版本、状态和失败原因。

## 6. M3：评测、安全与用户验证

目标：不仅证明“功能能跑”，还要证明Agent输出质量可测量。

任务：

- 实现批量Eval Runner，运行`evals/cases/`下的10个固定案例；
- 计算事实召回率、关键问题覆盖率、重复问题率和禁止项违反率；
- 对模型输出增加Schema、Prompt Injection、超时和敏感信息测试；
- 为API和工作流增加结构化日志、Trace ID和阶段耗时；
- 完成桌面端、移动端和失败状态的浏览器端到端测试；
- 邀请3名目标用户完成指定任务并记录反馈。

验收标准：

- 10个固定案例整体通过率不低于80%；
- Prompt Injection禁止项违反率为0；
- 核心API、定价公式和人工审批路径全部通过自动化测试；
- 浏览器控制台无错误，桌面端和移动端主链路可用；
- 至少2名测试用户认为生成结果对实际接单有帮助。

## 7. M4：部署与课程作业材料

目标：让老师或新用户无需了解代码也能访问、理解和演示项目。

任务：

- 部署前端、后端和SQLite兼容的持久化环境；
- 配置生产环境变量、CORS、健康检查和错误日志；
- 更新README中的功能、架构、启动、测试和部署说明；
- 准备核心页面截图、架构图、工作流图和评测结果图；
- 制作课程汇报PPT、项目海报和3-5分钟演示脚本；
- 录制“创建项目→AI澄清→生成报价→人工确认”的演示视频；
- 整理课程要求对应关系和最终提交清单。

验收标准：

- 公网链接可以完成核心流程；
- 新用户在10分钟内可以按README启动本地项目；
- 提交材料覆盖需求、Prompt工程、Agent编排、评测、代码和演示证据；
- Git仓库不包含密钥、本地数据库、客户隐私或依赖目录。

## 8. Git提交路线

| 提交 | 建议提交信息 | 内容 | 状态 |
|---|---|---|---|
| C0-C1 | 需求与架构基线 | PRD、Agent路线、工程骨架 | ✅ 已完成 |
| C2-C4 | `feat: complete intake and clarification workflow` | 评测契约、需求澄清Agent、前端工作台 | ✅ `0816ad0`已推送 |
| C5-A | `feat: add structured model gateway` | 真实模型、结构化输出、Fallback和调用记录 | 🔴 下一提交 |
| C5-B | `feat: orchestrate scope risk and pricing skills` | 剩余Skill、确定性报价Tool和方案页面 | ⬜ |
| C6 | `feat: persist resumable approval workflow` | SQLite、Checkpoint、幂等和人工审批 | ⬜ |
| C7 | `test: evaluate agent workflow end to end` | Eval Runner、安全、Trace和用户测试 | ⬜ |
| C8 | `docs: complete deployment and assignment materials` | 部署、README、PPT和演示材料 | ⬜ |

每次提交前至少执行：

```powershell
cd backend
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -q

cd ..\frontend
npm run build
```

涉及前后端联调的提交还必须通过一次真实浏览器主链路验证。

## 9. Agent工程能力学习映射

| Roadmap阶段 | 需要掌握的企业Agent能力 | 在本项目中的证据 |
|---|---|---|
| M1-A | Prompt、Structured Output、模型网关、Fallback | 两项Skill真实模型输出和Schema校验 |
| M1-B | Workflow、Skill编排、Tool Calling、确定性计算 | 六个Skill和报价Tool执行链 |
| M2 | State、Memory、Checkpoint、Human-in-the-loop、幂等 | 可恢复的SQLite状态和人工确认节点 |
| M3 | Eval、Trace、Observability、Guardrail、安全 | 指标报告、执行追踪和攻击案例 |
| M4 | 部署、密钥管理、产品表达和工程复盘 | 在线应用、README、PPT与演示视频 |

## 10. 下一步行动清单

接下来只执行M1-A，不同时展开数据库、RAG或多Agent：

- [x] 确认使用DeepSeek V4 Flash作为开发模型；
- [x] 实现模型网关配置与基础设施适配器；
- [x] 为需求提取和澄清Skill建立版本化Prompt；
- [x] 接入JSON Output与Pydantic Schema校验；
- [x] 实现超时、重试和规则Fallback；
- [x] 增加模型网关与两项Skill测试；
- [x] 在本地`backend/.env`配置真实DeepSeek API Key；
- [x] 完成DeepSeek线上最小调用Smoke Test；
- [ ] 运行10个固定案例并记录第一版模型结果；
- [ ] 浏览器回归“创建项目→AI分析→回答澄清问题”；
- [ ] 提交并推送C5-A。

M1-A通过验收后，再开始M1-B的范围、工时、风险、报价和方案生成。
