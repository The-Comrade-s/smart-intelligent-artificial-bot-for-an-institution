"""
Notification service. Other services call `notify_admins` when something
admin-worthy happens (new feedback, upload failure, new registration, etc),
per the ES-003 notification triggers.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import NotificationType, UserRole
from app.models.system import Notification
from app.models.user import User


async def notify_admins(
    db: AsyncSession, title: str, message: str, type_: NotificationType = NotificationType.INFO, link: str | None = None
) -> None:
    result = await db.execute(select(User.id).where(User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])))
    admin_ids = [row[0] for row in result.all()]
    for admin_id in admin_ids:
        db.add(Notification(user_id=admin_id, type=type_, title=title, message=message, link=link))
    # Caller is responsible for committing as part of its own transaction.
