"""
app/schemas/user.py
────────────────────
Pydantic v2 schemas for User authentication and registration.

Validation rules enforced server-side (not just frontend):
  - Email: RFC-5322 format via EmailStr
  - Password: 8–128 chars, must contain at least one letter AND one digit
  - Full name: 2–100 chars, cannot be blank/whitespace only
"""
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.base import ORMBase

# Characters not allowed in names (SQL injection / XSS protection beyond Pydantic)
_NAME_BLOCKED = re.compile(r"[<>\"'%;()&]")


class UserCreate(BaseModel):
    """Schema for POST /auth/register"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        has_letter = any(c.isalpha() for c in v)
        has_digit  = any(c.isdigit() for c in v)
        if not (has_letter and has_digit):
            raise ValueError("Password must contain at least one letter and one digit")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_clean(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Full name cannot be blank")
        if _NAME_BLOCKED.search(stripped):
            raise ValueError("Full name contains invalid characters")
        return stripped


class UserUpdate(BaseModel):
    """Schema for PUT /users/me — all fields optional"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)

    @field_validator("full_name")
    @classmethod
    def full_name_clean(cls, v):
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("Full name cannot be blank")
        if _NAME_BLOCKED.search(stripped):
            raise ValueError("Full name contains invalid characters")
        return stripped


class UserResponse(ORMBase):
    """Returned to the client. Never includes hashed_password."""
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """Returned by /auth/login"""
    access_token: str
    token_type: str = "bearer"
