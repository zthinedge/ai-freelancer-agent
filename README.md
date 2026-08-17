# 接单智策 - AI 自由职业接单助手

接单智策面向自由职业者与小型工作室，把客户的模糊描述转成可确认的需求、分层功能范围、任务工时、三级报价与验收清单，减少漏项、低估工时和反复改需求。

## 当前版本

MVP v0.1 已包含：

- 客户原始需求录入；
- AI／规则回退双模式需求分析；
- 缺失信息追问；
- MoSCoW 范围拆分；
- 任务工时与三级报价；
- 风险、假设及验收标准；
- SQLite 项目保存与历史记录；
- 响应式 Web 工作台。

没有配置大模型密钥时，系统自动使用可重复演示的规则引擎；配置兼容 OpenAI Chat Completions 的 API 后，会切换为真实 AI 结构化分析。

## 项目结构

```text
AI自由职业接单助手/
├─ backend/                 FastAPI + SQLite API
├─ frontend/                React + TypeScript + Vite
├─ docs/                    用户、PRD、任务与作业材料
└─ README.md
```

## 快速启动

### 后端

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

API 文档：`http://127.0.0.1:8000/docs`

### 前端

```powershell
cd frontend
npm install
npm run dev
```

前端地址：`http://127.0.0.1:5173`

## AI 配置

编辑 `backend/.env`：

```env
AI_API_KEY=
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4.1-mini
```

密钥为空时不会请求外部服务，适合作业现场稳定演示。

## 测试

```powershell
cd backend
pytest --cov=app --cov-report=term-missing

cd ..\frontend
npm run build
```

## 文档导航

- [目标用户分析](docs/01-目标用户分析.md)
- [产品需求文档 PRD](docs/02-产品需求文档-PRD.md)
- [功能拆解与开发计划](docs/03-功能拆解与开发计划.md)
- [课程作业交付规划](docs/04-课程作业交付规划.md)
