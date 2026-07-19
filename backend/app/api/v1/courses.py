"""
Course management routes.
Read access: any authenticated user. Write access: admin/super admin only.
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.academics import Course
from app.models.enums import UserRole
from app.schemas.academics import CourseCreate, CourseOut, CourseUpdate

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=list[CourseOut])
async def list_courses(
    level: str | None = Query(default=None),
    semester: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    stmt = select(Course)
    if level:
        stmt = stmt.where(Course.level == level)
    if semester:
        stmt = stmt.where(Course.semester == semester)
    if search:
        stmt = stmt.where(Course.title.ilike(f"%{search}%") | Course.code.ilike(f"%{search}%"))
    result = await db.execute(stmt.order_by(Course.code))
    courses = result.scalars().all()
    return [CourseOut.model_validate({**c.__dict__, "id": str(c.id)}) for c in courses]


@router.get("/{course_id}", response_model=CourseOut)
async def get_course(course_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    course = await db.get(Course, course_id)
    if not course:
        raise NotFoundError("Course not found")
    return CourseOut.model_validate({**course.__dict__, "id": str(course.id)})


@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    course = Course(**{**payload.model_dump(exclude={"department_id"}), "department_id": uuid.UUID(payload.department_id)})
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return CourseOut.model_validate({**course.__dict__, "id": str(course.id)})


@router.patch("/{course_id}", response_model=CourseOut)
async def update_course(
    course_id: uuid.UUID,
    payload: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    course = await db.get(Course, course_id)
    if not course:
        raise NotFoundError("Course not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    await db.commit()
    await db.refresh(course)
    return CourseOut.model_validate({**course.__dict__, "id": str(course.id)})


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    course = await db.get(Course, course_id)
    if not course:
        raise NotFoundError("Course not found")
    await db.delete(course)
    await db.commit()
