"""
Pydantic schema for Department (read-only for now — the department list is
small and stable; full CRUD can be added if multi-department support is needed).
"""
from pydantic import BaseModel


class DepartmentOut(BaseModel):
    id: str
    name: str
    faculty: str | None = None
    overview: str | None = None
    hod_name: str | None = None
    office_location: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None

    model_config = {"from_attributes": True}
