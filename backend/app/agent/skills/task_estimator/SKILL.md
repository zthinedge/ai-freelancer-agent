---
name: task_estimator
version: 0.1.0
description: 将已确认范围拆解为任务、依赖和工时区间
stage: estimation
allowed_tools: []
---

## 输入

项目范围、交付标准、期限和已有约束。

## 输出

WBS任务、依赖、工时区间、估算依据和不确定性。

## Guardrail

- 不直接生成金额；
- 工时以0.5小时为最小单位；
- 明确第三方依赖与缓冲时间。

## 评测

检查任务覆盖率、依赖合理性和工时可解释性。
