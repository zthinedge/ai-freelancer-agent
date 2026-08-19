from uuid import uuid4

import httpx
import pytest


@pytest.mark.anyio
async def test_project_analysis_flow(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        create_response = await client.post(
            "/api/v1/projects",
            json={
                "schema_version": "1.0.0",
                "name": "企业官网",
                "client_request": "需要制作一个中英文企业官网，支持手机访问，希望三周内上线。",
                "service_type": "website",
                "budget": {"amount": "12000.00", "currency": "CNY"},
                "deadline": "三周内",
                "hourly_rate": {"amount": "150.00", "currency": "CNY"},
            },
        )

        assert create_response.status_code == 201
        project = create_response.json()
        run = project["run"]
        assert run["status"] == "waiting_user"
        assert run["current_step"] == "clarification_planner"
        assert 3 <= len(run["state"]["pending_questions"]) <= 6
        assert run["state"]["intake"]["project_type"] == "website"

        list_response = await client.get("/api/v1/projects")
        assert list_response.status_code == 200
        assert [item["id"] for item in list_response.json()] == [project["id"]]

        run_response = await client.get(f"/api/v1/agent-runs/{run['id']}")
        assert run_response.status_code == 200
        assert run_response.json()["id"] == run["id"]

        answers = {
            question["field"]: f"已确认：{question['field']}"
            for question in run["state"]["pending_questions"]
        }
        answer_response = await client.post(
            f"/api/v1/agent-runs/{run['id']}/answers",
            json={"schema_version": "1.0.0", "answers": answers},
        )
        assert answer_response.status_code == 200
        updated_run = answer_response.json()
        assert updated_run["status"] == "completed"
        assert updated_run["state"]["pending_questions"] == []
        assert updated_run["state"]["clarification_approved"] is True


@pytest.mark.anyio
async def test_unknown_run_returns_stable_error_contract(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/agent-runs/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {
        "schema_version": "1.0.0",
        "error_code": "resource_not_found",
        "message": "Agent运行记录不存在",
        "trace_id": "not-provided",
    }


@pytest.mark.anyio
async def test_project_input_rejects_unknown_fields(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "测试项目",
                "client_request": "这是一个长度足够但包含未知字段的测试项目需求。",
                "hourly_rate": {"amount": "100.00", "currency": "CNY"},
                "unexpected": True,
            },
        )

    assert response.status_code == 422
    assert response.json()["schema_version"] == "1.0.0"
    assert response.json()["error_code"] == "invalid_request"
    assert "unexpected" in response.json()["message"]
