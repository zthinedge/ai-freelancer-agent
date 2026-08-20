import json

import httpx
import pytest
from app.application.contracts import CreateProjectCommand
from app.application.services import ProjectAnalysisService
from app.bootstrap.app_factory import create_app
from app.core.config import Settings
from app.infrastructure.ai.rule_based_intake import RuleBasedIntakeAgent
from app.infrastructure.mcp import build_mcp_server
from app.infrastructure.memory import SQLiteContextMemory
from app.infrastructure.persistence.sqlite import SQLiteProjectAnalysisStore
from mcp import Client


def _settings(database_url: str) -> Settings:
    return Settings(
        environment="test",
        cors_origins=[],
        ai_api_key=None,
        database_url=database_url,
        mcp_enabled=False,
    )


@pytest.mark.anyio
async def test_sqlite_memory_survives_application_restart(tmp_path):
    database_url = f"sqlite:///{(tmp_path / 'persistent.db').as_posix()}"
    first_app = create_app(_settings(database_url))
    transport = httpx.ASGITransport(app=first_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/v1/projects",
            json={
                "name": "数据看板",
                "client_request": "分析销售数据并制作一个可筛选的经营数据看板。",
                "service_type": "data_analysis",
                "hourly_rate": {"amount": "180.00", "currency": "CNY"},
            },
        )
    assert created.status_code == 201

    restarted_app = create_app(_settings(database_url))
    restarted_transport = httpx.ASGITransport(app=restarted_app)
    async with httpx.AsyncClient(
        transport=restarted_transport,
        base_url="http://test",
    ) as client:
        projects = await client.get("/api/v1/projects")

    assert projects.status_code == 200
    assert [item["id"] for item in projects.json()] == [created.json()["id"]]
    assert projects.json()[0]["run"]["state"]["pending_questions"]


@pytest.mark.anyio
async def test_local_rag_handles_chinese_and_replaces_same_source(tmp_path):
    memory = SQLiteContextMemory(tmp_path / "rag.db")
    await memory.remember(
        source_id="guide:data",
        title="数据分析交付指南",
        content="数据分析项目需要确认字段含义、缺失值、样本规模和最终交付格式。",
    )

    first = await memory.search("数据分析缺失值怎么处理")
    assert first
    assert first[0].source_id == "guide:data"

    await memory.remember(
        source_id="guide:data",
        title="数据项目新指南",
        content="数据项目现在重点检查隐私授权和异常值。",
    )
    replaced = await memory.search("样本规模")
    assert replaced == ()
    assert (await memory.search("隐私授权"))[0].title == "数据项目新指南"


@pytest.mark.anyio
async def test_mcp_exposes_only_read_only_project_and_rag_capabilities(tmp_path):
    store = SQLiteProjectAnalysisStore(tmp_path / "mcp.db")
    memory = SQLiteContextMemory(tmp_path / "mcp.db")
    await memory.remember(
        source_id="guide:quote",
        title="报价检查",
        content="响应式网站报价前需要确认部署范围、验收标准和修改轮次。",
    )
    service = ProjectAnalysisService(store, RuleBasedIntakeAgent(), memory)
    project = await service.create_project(
        CreateProjectCommand(
            name="作品集网站",
            client_request="制作一个响应式设计师作品集网站并提供部署说明。",
            service_type="website",
            hourly_rate={"amount": "150.00", "currency": "CNY"},
        )
    )
    server = build_mcp_server(store, memory)

    async with Client(server) as client:
        tools = await client.list_tools()
        assert {tool.name for tool in tools.tools} == {"search_knowledge", "list_projects"}

        search = await client.call_tool("search_knowledge", {"query": "报价范围"})
        assert search.is_error is False
        assert search.structured_content is not None
        assert search.structured_content["results"]

        listed = await client.call_tool("list_projects", {"limit": 10})
        assert listed.structured_content is not None
        assert listed.structured_content["projects"][0]["id"] == str(project.id)

        resource = await client.read_resource(f"project://{project.id}")
        payload = json.loads(resource.contents[0].text)
        assert payload["id"] == str(project.id)
        assert payload["run"]["state"]["retrieved_context"]
