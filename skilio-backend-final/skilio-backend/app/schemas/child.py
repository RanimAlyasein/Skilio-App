"""
app/schemas/child.py
────────────────────
Pydantic schemas for child profile management.
Age is hard-validated to the 4–17 range on the server side.
"""
import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.schemas.base import ORMBase

_NAME_BLOCKED = re.compile(r"[<>\"'%;()&]")


class ChildCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=4, le=17)
    avatar_url: Optional[str] = Field(None, max_length=500)

    @field_validator("display_name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("display_name cannot be blank")
        if _NAME_BLOCKED.search(stripped):
            raise ValueError("display_name contains invalid characters")
        return stripped

    @field_validator("avatar_url")
    @classmethod
    def validate_url(cls, v):
        if v and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("avatar_url must be a valid http/https URL")
        return v


class ChildUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=50)
    age: Optional[int] = Field(None, ge=4, le=17)
    avatar_url: Optional[str] = Field(None, max_length=500)


class ChildResponse(ORMBase):
    id: int
    parent_id: int
    display_name: str
    age: int
    avatar_url: Optional[str]
    total_xp: int
    is_active: bool
    created_at: datetime


class ChildSummaryResponse(ORMBase):
    id: int
    display_name: str
    age: int
    avatar_url: Optional[str]
    total_xp: int
