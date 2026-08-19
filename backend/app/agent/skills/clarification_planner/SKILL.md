---
name: clarification_planner
version: 0.1.0
description: 根据缺失信息生成少量高价值澄清问题
stage: clarification_planner
triggers: [intake_completed_with_missing_fields]
do_not_use_when: [intake_missing, no_missing_fields]
input_schema: app.agent.schemas.ClarificationPlannerInput
output_schema: app.agent.schemas.ClarificationPlannerOutput
allowed_tools: []
max_auto_repairs: 1
fallback: template_questions_by_service_type
human_checkpoint: true
evaluation_cases: [EVAL-001, EVAL-002, EVAL-003, EVAL-004, EVAL-005, EVAL-006, EVAL-007, EVAL-008, EVAL-009, EVAL-010]
---

## 触发条件

`requirement_intake`成功且存在缺失字段时执行。

## 禁用条件

需求提取结果缺失、Schema不合法，或没有任何待确认信息时不得执行。

## 输入

`ClarificationPlannerInput`：已知事实、缺失字段、项目类型和客户约束。

## 输出

`ClarificationPlannerOutput`：3-6个有优先级的问题，每题包含原因和对应缺失字段，并进入人工补充节点。

## Guardrail

- 不重复询问已经确认的信息；
- 优先询问影响范围、价格、期限、安全和验收的问题；
- 不以问题形式暗示未经证实的方案；
- 生成后必须暂停等待人工输入。

## 失败与降级

Schema失败时最多修复一次；仍失败则按服务类型加载确定性问题模板。模板也不可用时停止运行并请求人工处理。

## 评测

运行全部10个案例，检查问题相关性、重复率、关键缺失覆盖率和问题数量。
