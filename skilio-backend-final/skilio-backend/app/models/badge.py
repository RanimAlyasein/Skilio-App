"""
app/models/badge.py
────────────────────
Badge system — three models:

  Badge         — definition of an achievement (name, image, trigger rule)
  BadgeAward    — junction: records when a Child earned a Badge
  ModuleBadge   — junction: associates Badges with SkillModules
                  (e.g. "Stranger Safety Expert" badge belongs to the Stranger Safety module)
"""

import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, JSON, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


# ── Enumerations ──────────────────────────────────────────────────────────────

class BadgeTriggerType(str, enum.Enum):
    FIRST_LESSON     = "first_lesson"     # awarded after completing any 1 lesson
    LESSON_COUNT     = "lesson_count"     # awarded after N total lessons completed
    MODULE_COMPLETE  = "module_complete"  # awarded after all lessons in a module done
    XP_MILESTONE     = "xp_milestone"    # awarded when total_xp crosses a threshold
    SAFE_CHOICES     = "safe_choices"     # awarded after N safe choices in total


# ── Badge ─────────────────────────────────────────────────────────────────────

class Badge(Base, TimestampMixin):
    """Definition of a badge. Created by admins, evaluated against child stats."""

    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # What event/condition triggers this badge
    trigger_type: Mapped[BadgeTriggerType] = mapped_column(
        Enum(BadgeTriggerType),
        nullable=False,
    )

    # Threshold value for the trigger (e.g. 5 for "complete 5 lessons")
    trigger_value: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Optional bonus XP awarded alongside the badge
    xp_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ── Relationships ─────────────────────────────────────────────────────────
    awards: Mapped[list["BadgeAward"]] = relationship(
        "BadgeAward",
        back_populates="badge",
        cascade="all, delete-orphan",
    )

    module_badges: Mapped[list["ModuleBadge"]] = relationship(
        "ModuleBadge",
        back_populates="badge",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Badge id={self.id} name={self.name!r} trigger={self.trigger_type.value}>"


# ── BadgeAward ────────────────────────────────────────────────────────────────

class BadgeAward(Base):
    """Records when a specific child earned a specific badge."""

    __tablename__ = "badge_awards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    child_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("children.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    badge_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("badges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    awarded_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # Optional JSON context explaining why this was awarded
    # e.g. {"lesson_id": 3, "attempt_id": 7, "trigger": "module_complete"}
    trigger_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    child: Mapped["Child"] = relationship(  # type: ignore[name-defined]
        "Child",
        back_populates="badge_awards",
    )

    badge: Mapped["Badge"] = relationship(
        "Badge",
        back_populates="awards",
    )

    def __repr__(self) -> str:
        return f"<BadgeAward child={self.child_id} badge={self.badge_id}>"


# ── ModuleBadge ───────────────────────────────────────────────────────────────

class ModuleBadge(Base):
    """
    Association table: links a Badge to a SkillModule.

    Allows the same badge to be associated with multiple modules,
    and a module to have multiple badges (one for completion, one for
    all-safe-choices, etc.).
    """

    __tablename__ = "module_badges"

    module_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("skill_modules.id", ondelete="CASCADE"),
        primary_key=True,
    )

    badge_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("badges.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # True if earning this badge requires completing ALL lessons in the module
    is_completion_badge: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    module: Mapped["SkillModule"] = relationship(  # type: ignore[name-defined]
        "SkillModule",
        back_populates="module_badges",
    )

    badge: Mapped["Badge"] = relationship(
        "Badge",
        back_populates="module_badges",
    )

    def __repr__(self) -> str:
        return f"<ModuleBadge module={self.module_id} badge={self.badge_id}>"
