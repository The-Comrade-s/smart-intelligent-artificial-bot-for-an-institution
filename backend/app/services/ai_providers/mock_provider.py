"""
Mock provider: deterministic, offline responses so the whole chat pipeline
(persistence, streaming, knowledge retrieval, suggestions) can be built and
demoed before real API keys are added.

Set AI_PROVIDER_DEFAULT=mock (the default) to use this.
"""
import asyncio
from typing import AsyncIterator

from app.services.ai_providers.base import AIProvider, AIRequestConfig, AIResponse, ChatMessage


class MockProvider(AIProvider):
    name = "mock"

    def _canned_response(self, messages: list[ChatMessage]) -> str:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return (
            "This is a placeholder response from the COSIB mock AI provider "
            "(no live Gemini/OpenAI key configured yet).\n\n"
            f"You asked: \"{last_user.strip()}\"\n\n"
            "Once a real provider is configured in AI Configuration, this message "
            "will be replaced with an actual AI-generated answer, grounded in the "
            "department knowledge base where relevant."
        )

    async def generate(self, messages: list[ChatMessage], config: AIRequestConfig) -> AIResponse:
        await asyncio.sleep(0.15)  # simulate latency
        text = self._canned_response(messages)
        return AIResponse(content=text, tokens_used=len(text.split()), model="mock-1", provider=self.name)

    async def stream(self, messages: list[ChatMessage], config: AIRequestConfig) -> AsyncIterator[str]:
        text = self._canned_response(messages)
        for word in text.split(" "):
            await asyncio.sleep(0.02)
            yield word + " "

    async def health_check(self) -> bool:
        return True
