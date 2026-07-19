"""
Google Gemini provider.

Uses the plain REST API via httpx rather than the SDK, to keep the
dependency footprint small and behavior predictable.
"""
import json
from typing import AsyncIterator

import httpx

from app.core.config import settings
from app.services.ai_providers.base import AIProvider, AIProviderError, AIRequestConfig, AIResponse, ChatMessage

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, model: str = "gemini-1.5-flash"):
        self.model = model
        self.api_key = settings.GEMINI_API_KEY

    def _build_payload(self, messages: list[ChatMessage], config: AIRequestConfig) -> dict:
        # Gemini has no separate "system" role in the basic contents array;
        # system instructions go in a dedicated field.
        contents = [
            {"role": "model" if m.role == "assistant" else "user", "parts": [{"text": m.content}]}
            for m in messages
            if m.role != "system"
        ]
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": config.temperature,
                "maxOutputTokens": config.max_tokens,
            },
        }
        if config.system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": config.system_prompt}]}
        return payload

    async def generate(self, messages: list[ChatMessage], config: AIRequestConfig) -> AIResponse:
        if not self.api_key:
            raise AIProviderError("GEMINI_API_KEY is not configured")

        url = f"{GEMINI_API_BASE}/{self.model}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=self._build_payload(messages, config))
            if resp.status_code != 200:
                raise AIProviderError(f"Gemini error {resp.status_code}: {resp.text[:300]}")
            data = resp.json()

        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise AIProviderError(f"Unexpected Gemini response shape: {e}")

        usage = data.get("usageMetadata", {})
        return AIResponse(
            content=text,
            tokens_used=usage.get("totalTokenCount"),
            model=self.model,
            provider=self.name,
        )

    async def stream(self, messages: list[ChatMessage], config: AIRequestConfig) -> AsyncIterator[str]:
        if not self.api_key:
            raise AIProviderError("GEMINI_API_KEY is not configured")

        url = f"{GEMINI_API_BASE}/{self.model}:streamGenerateContent?alt=sse&key={self.api_key}"
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream("POST", url, json=self._build_payload(messages, config)) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    raise AIProviderError(f"Gemini error {resp.status_code}: {body[:300]}")
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    chunk = line[len("data:"):].strip()
                    if not chunk or chunk == "[DONE]":
                        continue
                    try:
                        parsed = json.loads(chunk)
                        text = parsed["candidates"][0]["content"]["parts"][0]["text"]
                        yield text
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

    async def health_check(self) -> bool:
        return bool(self.api_key)
