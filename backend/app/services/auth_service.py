"""
Authentication business logic, separated from the route layer so it can be
unit-tested and reused (e.g. by an admin "create user" flow).
"""
import hashlib
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.enums import AccountStatus, UserRole
from app.models.user import RefreshToken, User
from app.schemas.auth import LoginRequest, RegisterRequest


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def register_user(db: AsyncSession, payload: RegisterRequest) -> User:
    existing = await db.execute(
        select(User).where((User.email == payload.email) | (User.username == payload.username))
    )
    if existing.scalar_one_or_none():
        raise ConflictError("A user with this email or username already exists")

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        matric_number=payload.matric_number,
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, payload: LoginRequest) -> User:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")
    if user.status != AccountStatus.ACTIVE:
        raise UnauthorizedError("Account is not active. Contact an administrator.")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    return user


async def issue_tokens(db: AsyncSession, user: User, user_agent: str | None, ip: str | None) -> tuple[str, str]:
    access_token = create_access_token(subject=str(user.id), role=user.role)
    refresh_token, expires_at = create_refresh_token(subject=str(user.id))

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=_hash_token(refresh_token),
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip,
        )
    )
    await db.commit()
    return access_token, refresh_token


async def rotate_refresh_token(db: AsyncSession, refresh_token: str) -> tuple[str, str]:
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise UnauthorizedError("Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid token type")

    token_hash = _hash_token(refresh_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored = result.scalar_one_or_none()
    if not stored or stored.revoked:
        raise UnauthorizedError("Refresh token has been revoked")

    user_result = await db.execute(select(User).where(User.id == stored.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("User not found")

    stored.revoked = True  # rotate: old token is single-use
    new_access = create_access_token(subject=str(user.id), role=user.role)
    new_refresh, expires_at = create_refresh_token(subject=str(user.id))
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=_hash_token(new_refresh),
            expires_at=expires_at,
        )
    )
    await db.commit()
    return new_access, new_refresh


async def revoke_refresh_token(db: AsyncSession, refresh_token: str) -> None:
    token_hash = _hash_token(refresh_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored = result.scalar_one_or_none()
    if stored:
        stored.revoked = True
        await db.commit()
