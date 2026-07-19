"""
System settings routes. Admins manage arbitrary key-value application
settings (branding, contact info, maintenance mode, etc) without touching
code. A small public subset is exposed unauthenticated for the landing
page / frontend branding.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.system import ApplicationSetting
from app.schemas.settings import SettingOut, SettingUpsert

router = APIRouter(prefix="/settings", tags=["System Settings"])

PUBLIC_KEYS = {"app_name", "app_logo_url", "primary_color", "secondary_color", "support_email", "maintenance_mode"}


@router.get("/public", response_model=list[SettingOut])
async def public_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationSetting).where(ApplicationSetting.key.in_(PUBLIC_KEYS)))
    rows = result.scalars().all()
    return [SettingOut.model_validate(r) for r in rows]


@router.get("", response_model=list[SettingOut])
async def list_settings(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    result = await db.execute(select(ApplicationSetting).order_by(ApplicationSetting.key))
    return [SettingOut.model_validate(r) for r in result.scalars().all()]


@router.put("", response_model=SettingOut)
async def upsert_setting(
    payload: SettingUpsert,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    result = await db.execute(select(ApplicationSetting).where(ApplicationSetting.key == payload.key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = payload.value
        setting.value_json = payload.value_json
        setting.description = payload.description
    else:
        setting = ApplicationSetting(**payload.model_dump())
        db.add(setting)
    await db.commit()
    await db.refresh(setting)
    return SettingOut.model_validate(setting)
