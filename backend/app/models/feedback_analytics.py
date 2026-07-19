"""
Feedback and analytics event models.
"""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class Feedback(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "feedback"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5
    category: Mapped[str] = mapped_column(String(50), default="general", nullable=False)  # bug|suggestion|general
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    admin_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class AnalyticsEvent(Base, UUIDMixin, TimestampMixin):
    """
    Lightweight event log. Aggregated periodically into dashboard metrics
    (daily conversations, popular topics, provider usage, etc).
    """
    __tablename__ = "analytics_events"

    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
