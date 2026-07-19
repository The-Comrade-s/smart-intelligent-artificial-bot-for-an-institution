"""
Pydantic schemas for AI provider configuration (admin-managed).
"""
from pydantic import BaseModel, Field


class AIProviderSettingOut(BaseModel):
    id: str
    provider: str
    is_active: bool
    is_enabled: bool
    temperature: float
    max_tokens: int
    streaming_enabled: bool
    system_prompt: str | None = None

    model_config = {"from_attributes": True}


class AIProviderSettingUpdate(BaseModel):
    is_enabled: bool | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=64, le=8192)
    streaming_enabled: bool | None = None
    system_prompt: str | None = None


class ActivateProviderRequest(BaseModel):
    provider: str
