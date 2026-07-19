"""
AI configuration routes: list providers, view/update per-provider settings,
and switch which provider is active — all admin-only, all without touching
application code (per the ES-002 requirement).
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.core.exceptions import AppError, NotFoundError
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.system import AIProviderSetting
from app.schemas.ai_config import ActivateProviderRequest, AIProviderSettingOut, AIProviderSettingUpdate
from app.services.ai_providers.manager import AIManager

router = APIRouter(prefix="/ai", tags=["AI Configuration"])


@router.get("/providers", response_model=list[AIProviderSettingOut])
async def list_providers(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    result = await db.execute(select(AIProviderSetting))
    settings_rows = result.scalars().all()
    return [AIProviderSettingOut.model_validate({**s.__dict__, "id": str(s.id)}) for s in settings_rows]


@router.get("/providers/available")
async def available_providers(_=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN))):
    return {"providers": AIManager.available_providers()}


@router.patch("/providers/{provider_name}", response_model=AIProviderSettingOut)
async def update_provider_settings(
    provider_name: str,
    payload: AIProviderSettingUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    result = await db.execute(select(AIProviderSetting).where(AIProviderSetting.provider == provider_name))
    setting = result.scalar_one_or_none()
    if not setting:
        raise NotFoundError(f"No settings found for provider '{provider_name}'")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(setting, field, value)
    await db.commit()
    await db.refresh(setting)
    return AIProviderSettingOut.model_validate({**setting.__dict__, "id": str(setting.id)})


@router.post("/providers/activate", response_model=AIProviderSettingOut)
async def activate_provider(
    payload: ActivateProviderRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    if payload.provider not in AIManager.available_providers():
        raise AppError(f"Unknown provider '{payload.provider}'", code="UNKNOWN_PROVIDER", status_code=400)

    result = await db.execute(select(AIProviderSetting))
    all_settings = result.scalars().all()
    target = None
    for setting in all_settings:
        setting.is_active = setting.provider == payload.provider
        if setting.provider == payload.provider:
            target = setting

    if not target:
        raise NotFoundError(
            f"No settings row exists for provider '{payload.provider}' yet — run scripts/seed.py or create one first"
        )

    await db.commit()
    await db.refresh(target)
    return AIProviderSettingOut.model_validate({**target.__dict__, "id": str(target.id)})
