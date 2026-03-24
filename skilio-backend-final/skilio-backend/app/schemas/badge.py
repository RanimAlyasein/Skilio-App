"""
app/schemas/badge.py
─────────────────────
Pydantic schemas for badges, badge awards, and progress.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.badge import BadgeTriggerType
from app.schemas.base import ORMBase


# ── Badge ─────────────────────────────────────────────────────────────────────

class BadgeResponse(ORMBase):
    id: int
    name: str
    description: str
    image_url: Optional[str]
    trigger_type: BadgeTriggerType
    trigger_value: int
    xp_bonus: int
    is_active: bool


class BadgeAwardResponse(ORMBase):
    id: int
    child_id: int
    badge_id: int
    awarded_at: datetime
    badge: BadgeResponse


# ── Progress ──────────────────────────────────────────────────────────────────

class ProgressResponse(ORMBase):
    id: int
    child_id: int
    module_id: int
    lessons_completed: int
    total_lessons: int
    last_activity_at: datetime
    completion_percentage: float


class ModuleProgressResponse(BaseModel):
    """Progress for one module, enriched with module title — for dashboard display."""
    module_id: int
    module_title: str
    lessons_completed: int
    total_lessons: int
    completion_percentage: float
    last_activity_at: Optional[datetime]


# ── Child summary (parent dashboard) ─────────────────────────────────────────

class ChildDashboardResponse(BaseModel):
    """
    Everything needed for the parent's child detail page in one response.
    Avoids multiple round-trips from the frontend.
    """
    child_id: int
    display_name: str
    age: int
    avatar_url: Optional[str]
    total_xp: int
    module_progress: list[ModuleProgressResponse] = []
    badges_earned: list[BadgeAwardResponse] = []
    recent_attempt_count: int = 0
