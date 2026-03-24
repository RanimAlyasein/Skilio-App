"""
app/schemas/module.py
──────────────────────
Pydantic schemas for SkillModule and Lesson.

These are primarily read resources — children and parents browse them,
only admins create/edit them (future scope).
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import ORMBase


# ── SkillModule schemas ───────────────────────────────────────────────────────

class SkillModuleCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    age_min: int = Field(4, ge=4, le=17)
    age_max: int = Field(17, ge=4, le=17)
    order_index: int = Field(0, ge=0)


class SkillModuleResponse(ORMBase):
    id: int
    title: str
    description: str
    thumbnail_url: Optional[str]
    age_min: int
    age_max: int
    is_published: bool
    order_index: int
    created_at: datetime


class SkillModuleWithLessons(SkillModuleResponse):
    """Extended response that includes the lesson list — used on module detail page."""
    lessons: list["LessonResponse"] = []


# ── Lesson schemas ────────────────────────────────────────────────────────────

class LessonCreate(BaseModel):
    module_id: int
    title: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    xp_reward: int = Field(50, ge=0, le=500)
    order_index: int = Field(0, ge=0)


class LessonResponse(ORMBase):
    id: int
    module_id: int
    title: str
    description: Optional[str]
    xp_reward: int
    order_index: int
    entry_node_id: Optional[int]
    created_at: datetime


# Required for forward reference in SkillModuleWithLessons
SkillModuleWithLessons.model_rebuild()
