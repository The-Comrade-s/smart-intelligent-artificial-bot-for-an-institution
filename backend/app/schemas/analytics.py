"""
Pydantic schemas for the analytics dashboard.
"""
from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_students: int
    active_users: int
    total_conversations: int
    todays_conversations: int
    knowledge_articles: int
    faqs: int
    courses: int
    lecturers: int
    announcements: int
    average_response_time_ms: float | None = None


class TimeseriesPoint(BaseModel):
    date: str
    count: int


class ProviderUsagePoint(BaseModel):
    provider: str
    count: int


class TopFAQItem(BaseModel):
    question: str
    views: int


class TopArticleItem(BaseModel):
    title: str
    views: int
    category: str
