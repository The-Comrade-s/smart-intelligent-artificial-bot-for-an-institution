"""
Pydantic schemas for Event.
"""
from datetime import datetime

from pydantic import BaseModel


class EventCreate(BaseModel):
    title: str
    description: str | None = None
    venue: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    organizer: str | None = None
    registration_link: str | None = None
    attachments: list[str] | None = None


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    venue: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    organizer: str | None = None
    registration_link: str | None = None
    attachments: list[str] | None = None


class EventOut(BaseModel):
    id: str
    title: str
    description: str | None = None
    venue: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    organizer: str | None = None
    registration_link: str | None = None
    attachments: list[str] | None = None

    model_config = {"from_attributes": True}
