---
name: scope_designer
version: 0.1.0
description: 将已确认需求拆分为MoSCoW范围和明确排除项
stage: scope
allowed_tools: []
---

## 输入

已确认事实和用户补充答案。

## 输出

Must、Should、Could、Won't以及每项归类依据。

## Guardrail

- Must只保留核心闭环；
- Won't至少包含两个明确边界；
- 信息不足时不得继续估时。

## 评测

检查核心闭环完整性和范围蔓延风险。
