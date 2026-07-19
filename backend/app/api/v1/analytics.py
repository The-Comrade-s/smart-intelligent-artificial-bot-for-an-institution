"""
Analytics routes, admin-only. Backs the admin dashboard's stat cards and charts.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.schemas.analytics import DashboardStats, ProviderUsagePoint, TimeseriesPoint, TopArticleItem, TopFAQItem
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])
_admin_only = require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(db: AsyncSession = Depends(get_db), _=Depends(_admin_only)):
    return await analytics_service.dashboard_stats(db)


@router.get("/conversations-timeseries", response_model=list[TimeseriesPoint])
async def conversations_timeseries(
    days: int = Query(default=14, ge=1, le=90), db: AsyncSession = Depends(get_db), _=Depends(_admin_only)
):
    return await analytics_service.conversations_timeseries(db, days)


@router.get("/provider-usage", response_model=list[ProviderUsagePoint])
async def provider_usage(db: AsyncSession = Depends(get_db), _=Depends(_admin_only)):
    return await analytics_service.provider_usage(db)


@router.get("/user-growth", response_model=list[TimeseriesPoint])
async def user_growth(
    days: int = Query(default=30, ge=1, le=365), db: AsyncSession = Depends(get_db), _=Depends(_admin_only)
):
    return await analytics_service.user_growth(db, days)


@router.get("/top-faqs", response_model=list[TopFAQItem])
async def top_faqs(limit: int = Query(default=5, ge=1, le=20), db: AsyncSession = Depends(get_db), _=Depends(_admin_only)):
    return await analytics_service.top_faqs(db, limit)


@router.get("/top-articles", response_model=list[TopArticleItem])
async def top_articles(
    limit: int = Query(default=5, ge=1, le=20), db: AsyncSession = Depends(get_db), _=Depends(_admin_only)
):
    return await analytics_service.top_articles(db, limit)
