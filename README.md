# 接单智策 - AI自由职业接单助手

接单智策面向自由职业者与小型工作室，目标是把客户的模糊描述转成可确认的需求、范围、任务、风险和报价草案。AI负责理解与建议，确定性工具负责金额计算，人类负责最终承诺。

## 当前状态

当前为`v0.2 Architecture Baseline`，已完成P1架构骨架，尚未实现具体业务函数：

- 后端模块化单体与清洁架构边界；
- Agent状态、工作流、Skill、Tool和模型端口；
- 六个版本化Skill Manifest；
- 前端Feature分层与领域类型；
- 可启动的前后端架构占位页和健康检查；
- 后端依赖规则测试与Skill Manifest测试。

下一阶段P2将建立10个评测案例和稳定Schema；P3才开始实现需求提取与澄清Agent闭环。

## 架构概览

```text
React
  app -> pages -> features -> entities -> shared
                         |
                      REST API
                         |
FastAPI
  presentation -> application / agent -> domain
                         ^
              infrastructure adapters
```

选择模块化单体是为了兼顾工业级边界与5个开发日周期。模型、数据库、Trace和Tool可以替换，但MVP仍只需要一个前端和一个后端进程。

## 项目结构

```text
AI自由职业接单助手/
├─ backend/
│  ├─ app/
│  │  ├─ domain/             纯领域模型
│  │  ├─ application/        用例和外部端口
│  │  ├─ agent/              编排契约、工作流与Skills
│  │  ├─ infrastructure/     AI、存储、Trace和Tool插槽
│  │  ├─ presentation/       FastAPI HTTP适配层
│  │  ├─ bootstrap/          依赖装配
│  │  └─ core/               配置和错误
│  └─ tests/                 健康、依赖规则和Manifest测试
├─ frontend/
│  └─ src/
│     ├─ app/                应用入口
│     ├─ pages/              页面组合
│     ├─ features/           用户动作
│     ├─ entities/           稳定业务类型
│     └─ shared/             通用契约和UI
└─ docs/                     PRD、架构、进度和课程材料
```

## 本地启动

### 后端

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

- 健康检查：`http://127.0.0.1:8000/api/health`
- API文档：`http://127.0.0.1:8000/docs`

### 前端

```powershell
cd frontend
npm install
npm run dev
```

前端地址：`http://127.0.0.1:5173`

## 架构验证

```powershell
cd backend
ruff check app tests
pytest

cd ..\frontend
npm run build
```

## 环境变量

复制`backend/.env.example`到`backend/.env`。真实密钥只放在本地`.env`或部署平台密钥管理中，不得提交Git。

```env
APP_AI_API_KEY=
APP_AI_BASE_URL=https://api.openai.com/v1
APP_AI_MODEL=
```

P3会实现OpenAI兼容网关和无密钥Mock网关；当前版本不调用任何外部模型。

## 文档导航

- [目标用户分析](docs/01-目标用户分析.md)
- [产品需求文档 PRD](docs/02-产品需求文档-PRD.md)
- [功能拆解与开发计划](docs/03-功能拆解与开发计划.md)
- [课程作业交付规划](docs/04-课程作业交付规划.md)
- [AI Native Agent架构与学习路线](docs/05-AI-Native-Agent架构与学习路线.md)
- [开发流程与项目进度表](docs/06-开发流程与项目进度表.md)
- [系统架构设计](docs/07-系统架构设计.md)
