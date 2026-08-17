---
name: clarification_planner
version: 0.1.0
description: 根据缺失信息生成少量高价值澄清问题
stage: clarification
allowed_tools: []
---

## 输入

已知事实、缺失字段、项目类型和客户约束。

## 输出

3-6个有优先级的问题，每个问题包含原因和对应缺失字段。

## Guardrail

- 不重复询问已明确的信息；
- 优先影响范围、价格和交付时间的问题；
- 生成后进入人工补充节点。

## 评测

检查问题相关性、重复率和关键缺失覆盖率。
