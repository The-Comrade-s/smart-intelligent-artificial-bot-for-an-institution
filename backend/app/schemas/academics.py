"""
Pydantic schemas for Course, Lecturer, Department.
"""
from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    code: str = Field(max_length=20)
    title: str = Field(max_length=255)
    level: str
    semester: str
    units: int = 2
    description: str | None = None
    prerequisites: list[str] | None = None
    learning_outcomes: list[str] | None = None
    recommended_textbooks: list[str] | None = None
    department_id: str


class CourseUpdate(BaseModel):
    title: str | None = None
    level: str | None = None
    semester: str | None = None
    units: int | None = None
    description: str | None = None
    prerequisites: list[str] | None = None
    learning_outcomes: list[str] | None = None
    recommended_textbooks: list[str] | None = None


class CourseOut(BaseModel):
    id: str
    code: str
    title: str
    level: str
    semester: str
    units: int
    description: str | None = None
    prerequisites: list[str] | None = None
    learning_outcomes: list[str] | None = None
    recommended_textbooks: list[str] | None = None

    model_config = {"from_attributes": True}


class LecturerCreate(BaseModel):
    full_name: str
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    office: str | None = None
    office_hours: str | None = None
    research_interests: list[str] | None = None
    biography: str | None = None
    photo_url: str | None = None
    courses_taught: list[str] | None = None
    department_id: str


class LecturerOut(BaseModel):
    id: str
    full_name: str
    title: str | None = None
    email: str | None = None
    office: str | None = None
    office_hours: str | None = None
    research_interests: list[str] | None = None
    biography: str | None = None
    photo_url: str | None = None
    courses_taught: list[str] | None = None

    model_config = {"from_attributes": True}
