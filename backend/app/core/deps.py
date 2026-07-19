"""
Reusable FastAPI dependencies: current user resolution and RBAC guards.
"""
import uuid
from typing import Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        raise UnauthorizedError("Missing authentication token")
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedError("Invalid or expired token")

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    user_id = payload.get("sub")
    try:
        user_uuid = uuid.UUID(user_id)
    except (TypeError, ValueError):
        raise UnauthorizedError("Invalid token subject")

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("User not found")
    if user.status != "active":
        raise ForbiddenError("Account is not active")
    return user


def require_roles(*allowed_roles: UserRole) -> Callable:
    """
    Dependency factory for RBAC route protection.
    Usage: Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN))
    """

    async def _guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in {r.value for r in allowed_roles}:
            raise ForbiddenError("You do not have permission to access this resource")
        return current_user

    return _guard
