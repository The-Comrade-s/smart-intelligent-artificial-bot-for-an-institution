"""
Analytics aggregation service. Pulls real numbers from Users, Conversations,
Messages, Feedback, KnowledgeArticles, FAQs, and AnalyticsEvents — nothing
here is synthetic; if there's no data yet, counts are simply zero.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academics import Course, Lecturer
from app.models.chat import Conversation, Message
from app.models.content import FAQ, Announcement, KnowledgeArticle
from app.models.enums import AccountStatus, ContentStatus, UserRole
from app.models.user import User


async def dashboard_stats(db: AsyncSession) -> dict:
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total_students = (
        await db.execute(select(func.count(User.id)).where(User.role == UserRole.STUDENT))
    ).scalar_one()
    active_users = (
        await db.execute(select(func.count(User.id)).where(User.status == AccountStatus.ACTIVE))
    ).scalar_one()
    total_conversations = (await db.execute(select(func.count(Conversation.id)))).scalar_one()
    todays_conversations = (
        await db.execute(select(func.count(Conversation.id)).where(Conversation.created_at >= today_start))
    ).scalar_one()
    kb_articles = (
        await db.execute(select(func.count(KnowledgeArticle.id)).where(KnowledgeArticle.status == ContentStatus.PUBLISHED))
    ).scalar_one()
    faqs = (await db.execute(select(func.count(FAQ.id)).where(FAQ.status == ContentStatus.PUBLISHED))).scalar_one()
    courses = (await db.execute(select(func.count(Course.id)))).scalar_one()
    lecturers = (await db.execute(select(func.count(Lecturer.id)))).scalar_one()
    announcements = (
        await db.execute(select(func.count(Announcement.id)).where(Announcement.status == ContentStatus.PUBLISHED))
    ).scalar_one()
    avg_response_ms = (
        await db.execute(select(func.avg(Message.response_time_ms)).where(Message.response_time_ms.is_not(None)))
    ).scalar_one()

    return {
        "total_students": total_students,
        "active_users": active_users,
        "total_conversations": total_conversations,
        "todays_conversations": todays_conversations,
        "knowledge_articles": kb_articles,
        "faqs": faqs,
        "courses": courses,
        "lecturers": lecturers,
        "announcements": announcements,
        "average_response_time_ms": round(float(avg_response_ms), 0) if avg_response_ms else None,
    }


async def conversations_timeseries(db: AsyncSession, days: int = 14) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(func.date(Conversation.created_at), func.count(Conversation.id))
        .where(Conversation.created_at >= since)
        .group_by(func.date(Conversation.created_at))
        .order_by(func.date(Conversation.created_at))
    )
    return [{"date": str(row[0]), "count": row[1]} for row in result.all()]


async def provider_usage(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Conversation.ai_provider_used, func.count(Conversation.id))
        .where(Conversation.ai_provider_used.is_not(None))
        .group_by(Conversation.ai_provider_used)
    )
    return [{"provider": row[0], "count": row[1]} for row in result.all()]


async def user_growth(db: AsyncSession, days: int = 30) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(func.date(User.created_at), func.count(User.id))
        .where(User.created_at >= since)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
    )
    return [{"date": str(row[0]), "count": row[1]} for row in result.all()]


async def top_faqs(db: AsyncSession, limit: int = 5) -> list[dict]:
    result = await db.execute(select(FAQ).order_by(FAQ.view_count.desc()).limit(limit))
    return [{"question": f.question, "views": f.view_count} for f in result.scalars().all()]


async def top_articles(db: AsyncSession, limit: int = 5) -> list[dict]:
    result = await db.execute(select(KnowledgeArticle).order_by(KnowledgeArticle.view_count.desc()).limit(limit))
    return [{"title": a.title, "views": a.view_count, "category": a.category} for a in result.scalars().all()]
