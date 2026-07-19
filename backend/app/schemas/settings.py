"""
Pydantic schemas for ApplicationSetting (admin-editable key-value config).
"""
from pydantic import BaseModel


class SettingUpsert(BaseModel):
    key: str
    value: str | None = None
    value_json: dict | None = None
    description: str | None = None


class SettingOut(BaseModel):
    key: str
    value: str | None = None
    value_json: dict | None = None
    description: str | None = None

    model_config = {"from_attributes": True}
