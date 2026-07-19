"""
Notification center routes: list, mark read, unread count.
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.system import Notification
from app.models.user import User
from app.schemas.notifications import NotificationOut

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationOut])
async def list_notifications(
    unread_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    stmt = stmt.order_by(Notification.created_at.desc()).limit(100)
    result = await db.execute(stmt)
    return [NotificationOut.model_validate({**n.__dict__, "id": str(n.id)}) for n in result.scalars().all()]


@router.get("/unread-count")
async def unread_count(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id, Notification.is_read.is_(False)
        )
    )
    return {"unread_count": result.scalar_one()}


@router.patch("/{notification_id}/read", response_model=NotificationOut)
async def mark_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = await db.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise NotFoundError("Notification not found")
    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return NotificationOut.model_validate({**notification.__dict__, "id": str(notification.id)})


@router.patch("/read-all")
async def mark_all_read(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id, Notification.is_read.is_(False))
    )
    for n in result.scalars().all():
        n.is_read = True
    await db.commit()
    return {"success": True}
