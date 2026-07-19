"""
Audit log routes: read-only, filterable by action/resource/user.
Restricted to super administrators since this is the system's own trail.
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.system import AuditLog
from app.schemas.audit import AuditLogOut

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=list[AuditLogOut])
async def list_audit_logs(
    action: str | None = Query(default=None),
    user_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.SUPER_ADMIN)),
):
    stmt = select(AuditLog)
    if action:
        stmt = stmt.where(AuditLog.action.ilike(f"%{action}%"))
    if user_id:
        stmt = stmt.where(AuditLog.user_id == user_id)
    stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit)

    result = await db.execute(stmt)
    logs = result.scalars().all()
    return [
        AuditLogOut.model_validate({**log.__dict__, "id": str(log.id), "user_id": str(log.user_id) if log.user_id else None})
        for log in logs
    ]
