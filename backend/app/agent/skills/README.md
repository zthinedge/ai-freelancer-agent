# Skill目录约定

每个业务Skill独立放在一个目录中，`SKILL.md`定义用途、触发条件、禁用条件、输入输出、可用工具、Guardrail、失败策略和评测案例。P2只建立稳定契约，P3才实现首批运行时代码。

依赖规则：

- Skill输入输出必须引用`agent/schemas.py`中的严格Pydantic模型；
- Skill可以依赖`agent/contracts.py`中的结构化状态；
- Skill不得直接访问数据库、HTTP客户端或环境变量；
- 外部能力必须通过Tool或ModelGateway端口调用；
- Skill输出必须包含Schema、Prompt和Skill版本；
- Schema校验失败最多自动修复一次，之后必须Fallback或人工处理；
- Manifest引用的案例必须存在于项目根目录`evals/cases/`；
- 新Skill先有评测案例和契约，再实现代码，最后注册到主工作流。
