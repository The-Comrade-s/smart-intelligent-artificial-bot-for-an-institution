"""
Announcement routes. Published announcements are readable by any
authenticated user; creation/editing is admin-only.
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.content import Announcement
from app.models.enums import ContentStatus, UserRole
from app.schemas.content import AnnouncementCreate, AnnouncementOut

router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.get("", response_model=list[AnnouncementOut])
async def list_announcements(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(
        select(Announcement)
        .where(Announcement.status == ContentStatus.PUBLISHED)
        .order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc())
    )
    items = result.scalars().all()
    return [AnnouncementOut.model_validate({**a.__dict__, "id": str(a.id)}) for a in items]


@router.post("", response_model=AnnouncementOut, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    payload: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.LECTURER)),
):
    announcement = Announcement(**payload.model_dump(), created_by=current_user.id)
    db.add(announcement)
    await db.commit()
    await db.refresh(announcement)
    return AnnouncementOut.model_validate({**announcement.__dict__, "id": str(announcement.id)})


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    announcement_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    announcement = await db.get(Announcement, announcement_id)
    if not announcement:
        raise NotFoundError("Announcement not found")
    await db.delete(announcement)
    await db.commit()
