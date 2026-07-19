"""
Pydantic schema for AuditLog read access.
"""
from datetime import datetime

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: str
    user_id: str | None = None
    action: str
    resource_type: str | None = None
    resource_id: str | None = None
    ip_address: str | None = None
    status: str
    details: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
