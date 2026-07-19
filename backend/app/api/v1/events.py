"""
Event routes: department seminars, exams, SIWES orientation, meetings, etc.
Read: any authenticated user. Write: admin/lecturer.
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.content import Event
from app.models.enums import UserRole
from app.schemas.events import EventCreate, EventOut, EventUpdate

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=list[EventOut])
async def list_events(
    upcoming_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    stmt = select(Event)
    if upcoming_only:
        from datetime import datetime, timezone

        stmt = stmt.where(Event.start_time >= datetime.now(timezone.utc))
    result = await db.execute(stmt.order_by(Event.start_time))
    events = result.scalars().all()
    return [EventOut.model_validate({**e.__dict__, "id": str(e.id)}) for e in events]


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.LECTURER)),
):
    event = Event(**payload.model_dump())
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return EventOut.model_validate({**event.__dict__, "id": str(event.id)})


@router.patch("/{event_id}", response_model=EventOut)
async def update_event(
    event_id: uuid.UUID,
    payload: EventUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.LECTURER)),
):
    event = await db.get(Event, event_id)
    if not event:
        raise NotFoundError("Event not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    await db.commit()
    await db.refresh(event)
    return EventOut.model_validate({**event.__dict__, "id": str(event.id)})


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    event = await db.get(Event, event_id)
    if not event:
        raise NotFoundError("Event not found")
    await db.delete(event)
    await db.commit()
