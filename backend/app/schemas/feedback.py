"""
Pydantic schemas for Feedback.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    conversation_id: str | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    category: str = "general"  # bug | suggestion | general
    comment: str | None = None


class FeedbackRespond(BaseModel):
    admin_response: str


class FeedbackOut(BaseModel):
    id: str
    user_id: str | None = None
    conversation_id: str | None = None
    rating: int | None = None
    category: str
    comment: str | None = None
    admin_response: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackSummary(BaseModel):
    average_rating: float | None
    total_feedback: int
    positive_count: int
    negative_count: int
    bug_reports: int
    suggestions: int
