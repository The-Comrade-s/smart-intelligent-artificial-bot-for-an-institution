"""
Aggregates every v1 router into a single APIRouter mounted by main.py.
"""
from fastapi import APIRouter

from app.api.v1 import (
    admin,
    ai_config,
    analytics,
    announcements,
    audit_logs,
    auth,
    chat,
    conversations,
    courses,
    departments,
    documents,
    events,
    feedback,
    health,
    knowledge_base,
    lecturers,
    notifications,
    settings,
    users,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(departments.router)
api_router.include_router(courses.router)
api_router.include_router(lecturers.router)
api_router.include_router(announcements.router)

# ES-002: AI engine, chat, knowledge retrieval
api_router.include_router(chat.router)
api_router.include_router(conversations.router)
api_router.include_router(knowledge_base.router)
api_router.include_router(documents.router)
api_router.include_router(ai_config.router)

# ES-003: administration portal, department management, analytics
api_router.include_router(events.router)
api_router.include_router(feedback.router)
api_router.include_router(analytics.router)
api_router.include_router(settings.router)
api_router.include_router(audit_logs.router)
api_router.include_router(notifications.router)
api_router.include_router(admin.router)
