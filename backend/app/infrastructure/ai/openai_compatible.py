import asyncio
import json
from collections.abc import Mapping
from time import perf_counter
from typing import Any

import httpx

from app.agent.contracts import ModelRequest, ModelResponse
from app.agent.ports import ModelGateway


class ModelGatewayError(RuntimeError):
    """可安全降级的模型调用失败，不包含密钥或完整响应正文。"""


class RetryableModelGatewayError(ModelGatewayError):
    """适合在有限次数内重试的临时模型故障。"""


class OpenAICompatibleModelGateway(ModelGateway):
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float,
        max_retries: int,
        max_tokens: int,
        thinking_enabled: bool,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._endpoint = f"{base_url.rstrip('/')}/chat/completions"
        self._api_key = api_key
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._max_tokens = max_tokens
        self._thinking_enabled = thinking_enabled
        self._transport = transport

    async def complete(self, request: ModelRequest) -> ModelResponse:
        payload = self._build_payload(request)
        last_error: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                return await self._send(payload)
            except (
                httpx.TimeoutException,
                httpx.TransportError,
                RetryableModelGatewayError,
            ) as error:
                last_error = error
                if attempt >= self._max_retries:
                    break
                await asyncio.sleep(min(0.25 * (2**attempt), 1.0))

        raise ModelGatewayError("模型服务暂时不可用") from last_error

    def _build_payload(self, request: ModelRequest) -> dict[str, Any]:
        schema = json.dumps(request.output_schema, ensure_ascii=False, separators=(",", ":"))
        schema_instruction = (
            "必须仅返回一个json对象，并严格满足以下JSON Schema；不得增加Schema之外的字段：\n"
            f"{schema}"
        )
        messages = [message.model_dump(mode="json") for message in request.messages]
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = f"{messages[0]['content']}\n\n{schema_instruction}"
        else:
            messages.insert(0, {"role": "system", "content": schema_instruction})

        return {
            "model": self._model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": self._max_tokens,
            "response_format": {"type": "json_object"},
            "thinking": {"type": "enabled" if self._thinking_enabled else "disabled"},
            "stream": False,
        }

    async def _send(self, payload: Mapping[str, Any]) -> ModelResponse:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(
            timeout=self._timeout_seconds,
            transport=self._transport,
        ) as client:
            started_at = perf_counter()
            response = await client.post(self._endpoint, headers=headers, json=payload)
            latency_ms = round((perf_counter() - started_at) * 1000)

        if response.status_code == 429 or response.status_code >= 500:
            raise RetryableModelGatewayError(f"模型服务返回可重试状态 {response.status_code}")
        if response.is_error:
            raise ModelGatewayError(f"模型请求被拒绝（HTTP {response.status_code}）")

        try:
            body = response.json()
            choice = body["choices"][0]
            if choice.get("finish_reason") == "length":
                raise RetryableModelGatewayError("模型JSON输出被截断")
            content = choice["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise RetryableModelGatewayError("模型返回了空内容")
            parsed = json.loads(content)
            if not isinstance(parsed, dict):
                raise ModelGatewayError("模型返回的JSON不是对象")
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise RetryableModelGatewayError("无法解析模型JSON响应") from error

        usage = body.get("usage") if isinstance(body, dict) else None
        usage = usage if isinstance(usage, dict) else {}
        return ModelResponse(
            content=parsed,
            model=str(body.get("model") or self._model),
            input_tokens=_optional_int(usage.get("prompt_tokens")),
            output_tokens=_optional_int(usage.get("completion_tokens")),
            latency_ms=latency_ms,
        )


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None
