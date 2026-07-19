"""
Audit logging service. Call `log_action` from any route/service that
performs a sensitive or admin-facing mutation (user role changes, content
deletion, settings changes, AI config changes, etc).
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import AuditLog


async def log_action(
    db: AsyncSession,
    user_id: uuid.UUID | None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    ip_address: str | None = None,
    status: str = "success",
    details: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            status=status,
            details=details,
        )
    )
    # Intentionally not committing here — caller commits as part of its own
    # transaction so the audit entry and the mutation succeed/fail together.
