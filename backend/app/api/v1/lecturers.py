"""
Lecturer directory routes.
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.academics import Lecturer
from app.models.enums import UserRole
from app.schemas.academics import LecturerCreate, LecturerOut

router = APIRouter(prefix="/lecturers", tags=["Lecturers"])


@router.get("", response_model=list[LecturerOut])
async def list_lecturers(
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    stmt = select(Lecturer)
    if search:
        stmt = stmt.where(Lecturer.full_name.ilike(f"%{search}%"))
    result = await db.execute(stmt.order_by(Lecturer.full_name))
    lecturers = result.scalars().all()
    return [LecturerOut.model_validate({**l.__dict__, "id": str(l.id)}) for l in lecturers]


@router.get("/{lecturer_id}", response_model=LecturerOut)
async def get_lecturer(lecturer_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    lecturer = await db.get(Lecturer, lecturer_id)
    if not lecturer:
        raise NotFoundError("Lecturer not found")
    return LecturerOut.model_validate({**lecturer.__dict__, "id": str(lecturer.id)})


@router.post("", response_model=LecturerOut, status_code=status.HTTP_201_CREATED)
async def create_lecturer(
    payload: LecturerCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    lecturer = Lecturer(
        **{**payload.model_dump(exclude={"department_id"}), "department_id": uuid.UUID(payload.department_id)}
    )
    db.add(lecturer)
    await db.commit()
    await db.refresh(lecturer)
    return LecturerOut.model_validate({**lecturer.__dict__, "id": str(lecturer.id)})


@router.delete("/{lecturer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lecturer(
    lecturer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    lecturer = await db.get(Lecturer, lecturer_id)
    if not lecturer:
        raise NotFoundError("Lecturer not found")
    await db.delete(lecturer)
    await db.commit()
