"""
Department, Course, and Lecturer models.
"""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class Department(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    faculty: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    overview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hod_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    office_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    users: Mapped[list["User"]] = relationship(back_populates="department")
    courses: Mapped[list["Course"]] = relationship(back_populates="department", cascade="all, delete-orphan")
    lecturers: Mapped[list["Lecturer"]] = relationship(back_populates="department", cascade="all, delete-orphan")


class Course(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "courses"

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g. ND I, ND II, HND I, HND II
    semester: Mapped[str] = mapped_column(String(20), nullable=False)  # First | Second
    units: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prerequisites: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    learning_outcomes: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    recommended_textbooks: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)

    department: Mapped["Department"] = relationship(back_populates="courses")


class Lecturer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "lecturers"

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Mr, Mrs, Dr, Prof
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    office: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    office_hours: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    research_interests: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    courses_taught: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)

    department: Mapped["Department"] = relationship(back_populates="lecturers")
