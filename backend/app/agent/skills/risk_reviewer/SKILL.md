---
name: risk_reviewer
version: 0.1.0
description: 检查需求、技术、进度、隐私和商务风险
stage: risk_reviewer
triggers: [estimation_completed]
do_not_use_when: [scope_missing, estimate_missing]
input_schema: app.agent.schemas.RiskReviewerInput
output_schema: app.agent.schemas.RiskReviewerOutput
allowed_tools: []
max_auto_repairs: 1
fallback: static_risk_checklist
human_checkpoint: false
evaluation_cases: [EVAL-002, EVAL-003, EVAL-004, EVAL-005, EVAL-007, EVAL-008, EVAL-010]
---

## 触发条件

范围和任务估算都通过Schema后执行。

## 禁用条件

范围或估算缺失时不得执行，也不得脱离客户约束进行泛化风险罗列。

## 输入

`RiskReviewerInput`：已确认范围、任务计划、客户约束和外部依赖。

## 输出

`RiskReviewerOutput`：风险类别、严重程度、原因、影响、缓解措施和需人工决定事项。

## Guardrail

- 高风险项必须进入最终方案；
- 不提供法律结论或平台审核保证；
- 涉及敏感数据时必须给出脱敏、权限或部署提示；
- 对抗输入和未授权外部写操作必须标记为高风险。

## 失败与降级

Schema失败最多修复一次；仍失败则运行静态风险清单，并将未覆盖风险交给人工确认。

## 评测

检查关键风险召回率、严重度合理性、误报警比例和缓解措施可执行性。
