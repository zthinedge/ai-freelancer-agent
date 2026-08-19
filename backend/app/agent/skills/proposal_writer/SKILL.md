---
name: proposal_writer
version: 0.1.0
description: 将已验证结果整理为客户可读的报价方案草案
stage: proposal_writer
triggers: [pricing_completed]
do_not_use_when: [pricing_missing, scope_unconfirmed, high_risk_unresolved]
input_schema: app.agent.schemas.ProposalWriterInput
output_schema: app.agent.schemas.ProposalWriterOutput
allowed_tools: [pricing_calculator]
max_auto_repairs: 1
fallback: deterministic_proposal_template
human_checkpoint: true
evaluation_cases: [EVAL-001, EVAL-003, EVAL-004, EVAL-005, EVAL-007, EVAL-010]
---

## 触发条件

范围、任务、风险和`pricing_calculator`结果均有效时执行。

## 禁用条件

报价Tool结果缺失、范围未经确认，或高风险人工决策尚未完成时不得生成客户方案。

## 输入

`ProposalWriterInput`：项目名称、范围、任务、风险和报价Tool的确定性结果。

## 输出

`ProposalWriterOutput`：AI草案状态、项目摘要、交付范围、三级报价、排除项、验收方式和免责声明。

## Guardrail

- 金额只能逐字引用`pricing_calculator`结果，不得自行计算或修改；
- 未经人工确认必须标记为`ai_draft`；
- 不承诺结果、流量、销量、融资、审核或法律效力；
- 高风险项、排除项和验收标准不得省略。

## 失败与降级

Schema失败最多修复一次；仍失败则用确定性模板组合已验证字段，任何情况下都必须进入报价人工审批节点。

## 评测

检查金额一致性、边界完整性、风险保留、客户可读性和人工审批状态。
