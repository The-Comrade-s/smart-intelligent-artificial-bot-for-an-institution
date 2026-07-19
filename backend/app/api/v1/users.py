"""
User management routes (admin-facing). Self-service profile lives under /auth/me.
"""
import uuid

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.enums import AccountStatus, UserRole
from app.models.user import User
from app.schemas.auth import UserPublic
from app.services.audit_service import log_action

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserPublic])
async def list_users(
    role: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    if search:
        stmt = stmt.where(User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    result = await db.execute(stmt.order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [UserPublic.model_validate({**u.__dict__, "id": str(u.id)}) for u in users]


@router.patch("/{user_id}/status", response_model=UserPublic)
async def update_user_status(
    user_id: uuid.UUID,
    new_status: AccountStatus,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    user.status = new_status
    await log_action(
        db,
        current_user.id,
        action="user.status_updated",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
        details={"new_status": new_status.value if hasattr(new_status, "value") else new_status},
    )
    await db.commit()
    await db.refresh(user)
    return UserPublic.model_validate({**user.__dict__, "id": str(user.id)})


@router.patch("/{user_id}/role", response_model=UserPublic)
async def update_user_role(
    user_id: uuid.UUID,
    new_role: UserRole,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN)),
):
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    user.role = new_role
    await log_action(
        db,
        current_user.id,
        action="user.role_updated",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
        details={"new_role": new_role.value if hasattr(new_role, "value") else new_role},
    )
    await db.commit()
    await db.refresh(user)
    return UserPublic.model_validate({**user.__dict__, "id": str(user.id)})


@router.get("/{user_id}/login-history")
async def get_login_history(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    from app.models.user import RefreshToken

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.user_id == user_id).order_by(RefreshToken.created_at.desc()).limit(50)
    )
    tokens = result.scalars().all()
    return [
        {
            "logged_in_at": t.created_at.isoformat(),
            "ip_address": t.ip_address,
            "user_agent": t.user_agent,
            "revoked": t.revoked,
        }
        for t in tokens
    ]


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.SUPER_ADMIN)),
):
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    await db.delete(user)
    await db.commit()
