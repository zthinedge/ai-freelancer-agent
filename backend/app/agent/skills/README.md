# Skill目录约定

每个业务Skill独立放在一个目录中，`SKILL.md`定义用途、触发条件、输入输出、可用工具、Guardrail和评测案例。运行时代码将在P2-P3阶段实现；当前只建立稳定契约。

依赖规则：

- Skill可以依赖`agent/contracts.py`中的结构化状态；
- Skill不得直接访问数据库、HTTP客户端或环境变量；
- 外部能力必须通过Tool或ModelGateway端口调用；
- Skill输出必须是结构化数据；
- 新Skill先有评测案例，再注册到主工作流。
