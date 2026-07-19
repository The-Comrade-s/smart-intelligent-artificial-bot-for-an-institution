"""
Pydantic schemas for Announcement content.
"""
from datetime import datetime

from pydantic import BaseModel


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    audience: str = "all"
    priority: str = "normal"
    status: str = "draft"
    is_pinned: bool = False
    publish_at: datetime | None = None
    expires_at: datetime | None = None


class AnnouncementOut(BaseModel):
    id: str
    title: str
    content: str
    audience: str
    priority: str
    status: str
    is_pinned: bool
    publish_at: datetime | None = None
    expires_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
