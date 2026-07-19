"""
Department routes. Read access for any authenticated user (needed to
populate department pickers when creating courses/lecturers); editing the
HOD/contact fields is admin-only.
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.academics import Department
from app.models.enums import UserRole
from app.schemas.departments import DepartmentOut

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=list[DepartmentOut])
async def list_departments(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Department).order_by(Department.name))
    departments = result.scalars().all()
    return [DepartmentOut.model_validate({**d.__dict__, "id": str(d.id)}) for d in departments]


@router.patch("/{department_id}", response_model=DepartmentOut)
async def update_department(
    department_id: uuid.UUID,
    payload: DepartmentOut,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    department = await db.get(Department, department_id)
    if not department:
        raise NotFoundError("Department not found")
    for field, value in payload.model_dump(exclude={"id"}, exclude_unset=True).items():
        setattr(department, field, value)
    await db.commit()
    await db.refresh(department)
    return DepartmentOut.model_validate({**department.__dict__, "id": str(department.id)})
