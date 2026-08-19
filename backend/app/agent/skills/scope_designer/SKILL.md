---
name: scope_designer
version: 0.1.0
description: 将已确认需求拆分为MoSCoW范围和明确排除项
stage: scope_designer
triggers: [clarification_approved]
do_not_use_when: [clarification_pending, critical_information_missing]
input_schema: app.agent.schemas.ScopeDesignerInput
output_schema: app.agent.schemas.ScopeDesignerOutput
allowed_tools: []
max_auto_repairs: 1
fallback: manual_scope_required
human_checkpoint: false
evaluation_cases: [EVAL-001, EVAL-002, EVAL-003, EVAL-006, EVAL-009]
---

## 触发条件

澄清答案已由用户提交并确认，核心目标、用户、交付物和期限边界足以进入范围设计时执行。

## 禁用条件

人工澄清未完成或关键字段仍缺失时不得估算范围。

## 输入

`ScopeDesignerInput`：已确认事实和结构化澄清答案。

## 输出

`ScopeDesignerOutput`：Must、Should、Could、Won't及每项依据，包含是否仍被缺失信息阻塞。

## Guardrail

- Must只保留核心业务闭环；
- Won't至少包含两个明确边界；
- 不把预算上限自动转换为功能范围；
- 信息不足时设置阻塞状态，不继续估时。

## 失败与降级

Schema失败最多修复一次；仍失败则停止在范围节点，由用户手动确认Must与Won't。

## 评测

检查核心闭环完整性、Won't边界、范围蔓延率和对模糊需求的阻塞行为。
