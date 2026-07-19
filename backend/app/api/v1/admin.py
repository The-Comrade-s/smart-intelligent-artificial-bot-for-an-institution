"""
Admin-only convenience routes: a single "overview" payload for the
dashboard landing page, and a roles/permissions reference for the admin UI.

RBAC itself is enforced by `require_roles` on each route (see
app.core.deps) -- this endpoint documents that behavior, backed by
app.core.permissions.get_role_permissions(), which is the single place a
future granular/per-user permissions system would need to change.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.core.permissions import ROLE_HIERARCHY, get_role_permissions
from app.db.session import get_db
from app.models.enums import UserRole
from app.services import analytics_service

router = APIRouter(prefix="/admin", tags=["Admin"])
_admin_only = require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)


@router.get("/roles")
async def list_roles(_=Depends(_admin_only)):
    return [{"role": role, "permissions": get_role_permissions(role)} for role in ROLE_HIERARCHY]


@router.get("/overview")
async def admin_overview(db: AsyncSession = Depends(get_db), _=Depends(_admin_only)):
    stats = await analytics_service.dashboard_stats(db)
    top_faqs = await analytics_service.top_faqs(db, limit=5)
    top_articles = await analytics_service.top_articles(db, limit=5)
    provider_usage = await analytics_service.provider_usage(db)

    return {
        "stats": stats,
        "top_faqs": top_faqs,
        "top_articles": top_articles,
        "provider_usage": provider_usage,
    }
