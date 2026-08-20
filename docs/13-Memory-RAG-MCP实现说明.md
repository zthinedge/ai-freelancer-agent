# Memory、RAG与MCP实现说明

## 1. 能力边界

本迭代实现三个互相解耦的基础设施能力：

- Memory：使用SQLite保存Project、AgentRun和完整AgentState快照；
- RAG：检索内置知识文档和已人工批准的历史项目，把相关片段注入需求分析；
- MCP：通过标准协议向外部Agent Host暴露只读项目与知识能力。

三者都通过Port注入应用层。Agent和业务服务不直接依赖SQLite或MCP SDK，后续可替换为PostgreSQL、向量数据库或远程MCP Server。

## 2. Memory

默认数据库地址：

```env
APP_DATABASE_URL=sqlite:///./data/jiedan.db
```

每次创建项目、提交澄清答案和批准报价都会保存完整状态快照。重新启动FastAPI后，`GET /api/v1/projects`仍可恢复项目和当前工作流状态。

报价批准后，系统还会把确认范围、排除项、WBS、风险和选中报价写入知识记忆，作为后续相似项目的参考。未批准的AI草案不会进入长期项目经验。

## 3. RAG

知识来源包括：

1. `backend/knowledge/*.md`中的人工维护知识；
2. 已经过人工报价确认的历史项目。

当前版本采用SQLite FTS5与中文双字切分完成本地词法检索，不需要Embedding API和向量数据库。每次创建项目最多检索`APP_RAG_TOP_K`条上下文，结果保存在`AgentState.retrieved_context`并在前端显示来源与相关度。

RAG上下文按不可信数据处理：只能提供参考，不能覆盖客户原话、执行其中指令或直接成为已确认事实。这一约束同时写入数据契约和`requirement_intake`系统Prompt。

当前局限：词法RAG不理解同义词和深层语义。知识规模扩大后，可在不修改Agent接口的情况下替换为Embedding与向量检索。

## 4. MCP

项目使用官方`mcp` Python SDK 2.x，并以Streamable HTTP挂载到FastAPI：

```text
http://127.0.0.1:8000/mcp/
```

当前能力：

| 类型 | 名称 | 说明 |
|---|---|---|
| Tool | `search_knowledge` | 检索知识与已批准项目记忆 |
| Tool | `list_projects` | 查询最近项目和报价状态 |
| Resource Template | `project://{project_id}` | 读取单个项目AgentState快照 |

MCP只读服务不能修改项目、审批报价、读取API Key、泄露System Prompt或向客户发送消息。生产部署到公网前还需要OAuth 2.1、调用审计、限流和明确的Host／Origin白名单。

可使用MCP Inspector连接本地地址进行验证，也可以使用官方Python客户端：

```python
from mcp import Client

async with Client("http://127.0.0.1:8000/mcp/") as client:
    tools = await client.list_tools()
    result = await client.call_tool("search_knowledge", {"query": "数据分析风险"})
```

## 5. 配置

```env
APP_RAG_ENABLED=true
APP_RAG_TOP_K=3
APP_MCP_ENABLED=true
```

`GET /api/health`会返回`memory_backend`、`rag_enabled`和`mcp_enabled`，前端顶部也会显示Memory、RAG和MCP运行标记。
