import json

import httpx
import pytest
from app.agent.contracts import ModelMessage, ModelRequest
from app.infrastructure.ai.openai_compatible import OpenAICompatibleModelGateway


@pytest.mark.anyio
async def test_gateway_sends_server_side_key_and_parses_json_response():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://api.deepseek.com/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-secret"
        payload = json.loads(request.content)
        assert payload["model"] == "deepseek-v4-flash"
        assert payload["response_format"] == {"type": "json_object"}
        assert payload["thinking"] == {"type": "disabled"}
        assert "JSON Schema" in payload["messages"][0]["content"]
        return httpx.Response(
            200,
            json={
                "model": "deepseek-v4-flash",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": '{"result":"ok"}'},
                    }
                ],
                "usage": {"prompt_tokens": 12, "completion_tokens": 4},
            },
        )

    gateway = OpenAICompatibleModelGateway(
        base_url="https://api.deepseek.com",
        api_key="test-secret",
        model="deepseek-v4-flash",
        timeout_seconds=1,
        max_retries=0,
        max_tokens=1024,
        thinking_enabled=False,
        transport=httpx.MockTransport(handler),
    )

    response = await gateway.complete(
        ModelRequest(
            messages=[ModelMessage(role="system", content="请输出json")],
            output_schema={"type": "object"},
        )
    )

    assert response.content == {"result": "ok"}
    assert response.model == "deepseek-v4-flash"
    assert response.input_tokens == 12
    assert response.output_tokens == 4


@pytest.mark.anyio
async def test_gateway_retries_transient_server_error():
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(503, json={"error": "busy"})
        return httpx.Response(
            200,
            json={
                "model": "deepseek-v4-pro",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": '{"result":"recovered"}'},
                    }
                ],
            },
        )

    gateway = OpenAICompatibleModelGateway(
        base_url="https://api.deepseek.com",
        api_key="test-secret",
        model="deepseek-v4-pro",
        timeout_seconds=1,
        max_retries=1,
        max_tokens=1024,
        thinking_enabled=False,
        transport=httpx.MockTransport(handler),
    )

    response = await gateway.complete(
        ModelRequest(
            messages=[ModelMessage(role="user", content="json")],
            output_schema={"type": "object"},
        )
    )

    assert attempts == 2
    assert response.content == {"result": "recovered"}
