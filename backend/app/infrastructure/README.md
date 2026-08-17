# Infrastructure适配器约定

该层将在后续阶段承载可替换实现，不向领域层暴露SDK细节：

- `ai/`：OpenAI兼容模型网关和Mock网关；
- `persistence/`：SQLite仓储、Unit of Work和迁移；
- `observability/`：Trace、指标和结构化日志；
- `tools/`：确定性报价工具及未来MCP适配器。

适配器必须实现`application/ports.py`或`agent/ports.py`中的Protocol。HTTP层不得直接导入此目录；具体实现只在`bootstrap/`装配。
