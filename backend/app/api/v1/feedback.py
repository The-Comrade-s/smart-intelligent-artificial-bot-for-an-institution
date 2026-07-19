"""
Feedback routes. Any authenticated user can submit feedback; admins review,
respond, and see the aggregate summary that powers the analytics dashboard.
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.enums import NotificationType, UserRole
from app.models.feedback_analytics import Feedback
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackOut, FeedbackRespond, FeedbackSummary
from app.services.notification_service import notify_admins

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    payload: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    feedback = Feedback(
        user_id=current_user.id,
        conversation_id=uuid.UUID(payload.conversation_id) if payload.conversation_id else None,
        rating=payload.rating,
        category=payload.category,
        comment=payload.comment,
    )
    db.add(feedback)
    await notify_admins(
        db,
        title="New feedback received",
        message=f"{current_user.full_name} submitted {payload.category} feedback"
        + (f" ({payload.rating}\u2605)" if payload.rating else ""),
        type_=NotificationType.INFO if payload.category != "bug" else NotificationType.WARNING,
    )
    await db.commit()
    await db.refresh(feedback)
    return FeedbackOut.model_validate(
        {**feedback.__dict__, "id": str(feedback.id), "user_id": str(feedback.user_id),
         "conversation_id": str(feedback.conversation_id) if feedback.conversation_id else None}
    )


@router.get("", response_model=list[FeedbackOut])
async def list_feedback(
    category: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    stmt = select(Feedback)
    if category:
        stmt = stmt.where(Feedback.category == category)
    result = await db.execute(stmt.order_by(Feedback.created_at.desc()))
    items = result.scalars().all()
    return [
        FeedbackOut.model_validate(
            {**f.__dict__, "id": str(f.id), "user_id": str(f.user_id) if f.user_id else None,
             "conversation_id": str(f.conversation_id) if f.conversation_id else None}
        )
        for f in items
    ]


@router.get("/summary", response_model=FeedbackSummary)
async def feedback_summary(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    result = await db.execute(select(func.avg(Feedback.rating), func.count(Feedback.id)))
    avg_rating, total = result.one()

    positive = (
        await db.execute(select(func.count(Feedback.id)).where(Feedback.rating >= 4))
    ).scalar_one()
    negative = (
        await db.execute(select(func.count(Feedback.id)).where(Feedback.rating <= 2))
    ).scalar_one()
    bugs = (
        await db.execute(select(func.count(Feedback.id)).where(Feedback.category == "bug"))
    ).scalar_one()
    suggestions = (
        await db.execute(select(func.count(Feedback.id)).where(Feedback.category == "suggestion"))
    ).scalar_one()

    return FeedbackSummary(
        average_rating=round(float(avg_rating), 2) if avg_rating is not None else None,
        total_feedback=total or 0,
        positive_count=positive,
        negative_count=negative,
        bug_reports=bugs,
        suggestions=suggestions,
    )


@router.patch("/{feedback_id}/respond", response_model=FeedbackOut)
async def respond_to_feedback(
    feedback_id: uuid.UUID,
    payload: FeedbackRespond,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    feedback = await db.get(Feedback, feedback_id)
    if not feedback:
        raise NotFoundError("Feedback not found")
    feedback.admin_response = payload.admin_response
    await db.commit()
    await db.refresh(feedback)
    return FeedbackOut.model_validate(
        {**feedback.__dict__, "id": str(feedback.id), "user_id": str(feedback.user_id) if feedback.user_id else None,
         "conversation_id": str(feedback.conversation_id) if feedback.conversation_id else None}
    )
