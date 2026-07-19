"""
Content models: KnowledgeArticle, FAQ, Announcement, Event.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin
from app.models.enums import AnnouncementPriority, ContentStatus


class KnowledgeArticle(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "knowledge_articles"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    keywords: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    related_topics: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[ContentStatus] = mapped_column(String(20), default=ContentStatus.DRAFT, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class FAQ(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "faqs"

    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    helpful_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    not_helpful_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[ContentStatus] = mapped_column(String(20), default=ContentStatus.PUBLISHED, nullable=False)


class Announcement(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "announcements"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    audience: Mapped[str] = mapped_column(String(50), default="all", nullable=False)  # all|student|lecturer
    priority: Mapped[AnnouncementPriority] = mapped_column(
        String(20), default=AnnouncementPriority.NORMAL, nullable=False
    )
    status: Mapped[ContentStatus] = mapped_column(String(20), default=ContentStatus.DRAFT, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attachments: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    publish_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class Event(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    organizer: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    registration_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    attachments: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
