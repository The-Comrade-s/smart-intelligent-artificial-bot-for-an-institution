"""
Pydantic schemas for Notification.
"""
from datetime import datetime

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: str
    type: str
    title: str
    message: str
    is_read: bool
    link: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
