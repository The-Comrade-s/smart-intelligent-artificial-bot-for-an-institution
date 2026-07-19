"""
Provider-agnostic interface every AI backend must implement.

Adding a new provider means implementing this interface and registering it
in AIManager — no other application code changes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class AIResponse:
    content: str
    tokens_used: int | None = None
    model: str | None = None
    provider: str | None = None


@dataclass
class AIRequestConfig:
    temperature: float = 0.7
    max_tokens: int = 1024
    system_prompt: str = ""
    extra: dict = field(default_factory=dict)


class AIProviderError(Exception):
    """Raised when a provider fails to generate a response."""


class AIProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def generate(self, messages: list[ChatMessage], config: AIRequestConfig) -> AIResponse:
        """Return a complete response (non-streaming)."""

    @abstractmethod
    async def stream(self, messages: list[ChatMessage], config: AIRequestConfig) -> AsyncIterator[str]:
        """Yield response text incrementally."""

    async def health_check(self) -> bool:
        """Cheap check that the provider is reachable/configured. Override if needed."""
        return True
