"""
AIManager resolves which provider to use at request time, based on the
AIProviderSetting stored in the database (admin-configurable), falling back
to AI_PROVIDER_DEFAULT from environment config if nothing is set yet.

This is the single point of contact the rest of the app should use —
route handlers and services never import a concrete provider directly.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.system import AIProviderSetting
from app.services.ai_providers.base import AIProvider, AIRequestConfig
from app.services.ai_providers.gemini_provider import GeminiProvider
from app.services.ai_providers.mock_provider import MockProvider
from app.services.ai_providers.openai_provider import OpenAIProvider

_PROVIDER_REGISTRY: dict[str, type[AIProvider]] = {
    "mock": MockProvider,
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
}


class AIManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_provider_setting(self) -> AIProviderSetting | None:
        result = await self.db.execute(select(AIProviderSetting).where(AIProviderSetting.is_active.is_(True)))
        return result.scalar_one_or_none()

    async def resolve_provider(self) -> tuple[AIProvider, AIRequestConfig]:
        """
        Returns the configured provider instance plus its AIRequestConfig
        (temperature, max_tokens, system_prompt), pulled from the DB when an
        admin has configured one, otherwise sensible defaults.
        """
        db_setting = await self.get_active_provider_setting()

        provider_name = db_setting.provider if db_setting else settings.AI_PROVIDER_DEFAULT
        provider_cls = _PROVIDER_REGISTRY.get(provider_name, MockProvider)

        # Provider unusable (no key) -> fall back to mock so the app never hard-fails.
        provider = provider_cls()
        if not await provider.health_check():
            provider = MockProvider()

        config = AIRequestConfig(
            temperature=db_setting.temperature if db_setting else 0.7,
            max_tokens=db_setting.max_tokens if db_setting else 1024,
            system_prompt=db_setting.system_prompt if db_setting and db_setting.system_prompt else "",
        )
        return provider, config

    @staticmethod
    def available_providers() -> list[str]:
        return list(_PROVIDER_REGISTRY.keys())
