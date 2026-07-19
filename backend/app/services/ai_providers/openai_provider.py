"""
OpenAI provider, using the Chat Completions REST API directly via httpx.
"""
import json
from typing import AsyncIterator

import httpx

from app.core.config import settings
from app.services.ai_providers.base import AIProvider, AIProviderError, AIRequestConfig, AIResponse, ChatMessage

OPENAI_API_BASE = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = settings.OPENAI_API_KEY

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def _build_payload(self, messages: list[ChatMessage], config: AIRequestConfig, stream: bool) -> dict:
        chat_messages = []
        if config.system_prompt:
            chat_messages.append({"role": "system", "content": config.system_prompt})
        chat_messages.extend({"role": m.role, "content": m.content} for m in messages if m.role != "system")

        return {
            "model": self.model,
            "messages": chat_messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "stream": stream,
        }

    async def generate(self, messages: list[ChatMessage], config: AIRequestConfig) -> AIResponse:
        if not self.api_key:
            raise AIProviderError("OPENAI_API_KEY is not configured")

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                OPENAI_API_BASE, headers=self._headers(), json=self._build_payload(messages, config, stream=False)
            )
            if resp.status_code != 200:
                raise AIProviderError(f"OpenAI error {resp.status_code}: {resp.text[:300]}")
            data = resp.json()

        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise AIProviderError(f"Unexpected OpenAI response shape: {e}")

        usage = data.get("usage", {})
        return AIResponse(
            content=text,
            tokens_used=usage.get("total_tokens"),
            model=self.model,
            provider=self.name,
        )

    async def stream(self, messages: list[ChatMessage], config: AIRequestConfig) -> AsyncIterator[str]:
        if not self.api_key:
            raise AIProviderError("OPENAI_API_KEY is not configured")

        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST", OPENAI_API_BASE, headers=self._headers(), json=self._build_payload(messages, config, stream=True)
            ) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    raise AIProviderError(f"OpenAI error {resp.status_code}: {body[:300]}")
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    chunk = line[len("data:"):].strip()
                    if not chunk or chunk == "[DONE]":
                        continue
                    try:
                        parsed = json.loads(chunk)
                        delta = parsed["choices"][0]["delta"].get("content")
                        if delta:
                            yield delta
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

    async def health_check(self) -> bool:
        return bool(self.api_key)
