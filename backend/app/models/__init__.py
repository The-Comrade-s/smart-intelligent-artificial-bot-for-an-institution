"""
Import every model here so Alembic's autogenerate can discover them
via Base.metadata.
"""
from app.db.base_class import Base  # noqa: F401
from app.models.user import User, RefreshToken  # noqa: F401
from app.models.academics import Department, Course, Lecturer  # noqa: F401
from app.models.content import KnowledgeArticle, FAQ, Announcement, Event  # noqa: F401
from app.models.chat import Conversation, Message  # noqa: F401
from app.models.feedback_analytics import Feedback, AnalyticsEvent  # noqa: F401
from app.models.system import (  # noqa: F401
    AIProviderSetting,
    ApplicationSetting,
    AuditLog,
    Notification,
)

__all__ = [
    "Base",
    "User",
    "RefreshToken",
    "Department",
    "Course",
    "Lecturer",
    "KnowledgeArticle",
    "FAQ",
    "Announcement",
    "Event",
    "Conversation",
    "Message",
    "Feedback",
    "AnalyticsEvent",
    "AIProviderSetting",
    "ApplicationSetting",
    "AuditLog",
    "Notification",
]
