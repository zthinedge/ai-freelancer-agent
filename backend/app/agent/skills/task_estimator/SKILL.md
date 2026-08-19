---
name: task_estimator
version: 0.1.0
description: 将已确认范围拆解为任务、依赖和工时区间
stage: task_estimator
triggers: [scope_confirmed]
do_not_use_when: [scope_missing, scope_blocked]
input_schema: app.agent.schemas.TaskEstimatorInput
output_schema: app.agent.schemas.TaskEstimatorOutput
allowed_tools: []
max_auto_repairs: 1
fallback: manual_estimation_required
human_checkpoint: false
evaluation_cases: [EVAL-001, EVAL-004, EVAL-007, EVAL-008]
---

## 触发条件

MoSCoW范围、交付标准和主要外部约束已确认时执行。

## 禁用条件

范围不存在、仍被缺失信息阻塞，或验收标准为空时不得执行。

## 输入

`TaskEstimatorInput`：项目范围、验收标准、期限和外部约束。

## 输出

`TaskEstimatorOutput`：WBS任务、依赖、0.5小时粒度的工时区间、估算依据、缓冲和不确定性。

## Guardrail

- 不直接生成金额；
- 工时以0.5小时为最小单位，最大值不得小于最小值；
- 明确第三方依赖、返工缓冲和估算依据；
- Won't范围不得进入任务清单。

## 失败与降级

Schema或工时范围校验失败时最多修复一次；仍失败则要求人工估时，不调用报价Tool。

## 评测

检查任务覆盖率、依赖合理性、工时可解释性、粒度和排除项泄漏。
