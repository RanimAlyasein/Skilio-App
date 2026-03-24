"""
app/models/module.py
─────────────────────
SkillModule ORM model — a top-level subject category.

Examples: "Stranger Safety", "Fire Safety", "Road Safety"

Relationships:
  SkillModule  →  Lesson       (one-to-many)
  SkillModule  ↔  Badge        (many-to-many via ModuleBadge)
  SkillModule  →  Progress     (one-to-many: one Progress row per child per module)
"""

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class SkillModule(Base, TimestampMixin):
    __tablename__ = "skill_modules"

    # ── Primary key ───────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── Fields ────────────────────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(100), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Age range for content filtering
    age_min: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    age_max: Mapped[int] = mapped_column(Integer, default=17, nullable=False)

    # Only published modules are shown to children
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Controls display order in the module browser
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ── Relationships ─────────────────────────────────────────────────────────
    lessons: Mapped[list["Lesson"]] = relationship(  # type: ignore[name-defined]
        "Lesson",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="Lesson.order_index",
    )

    progress_records: Mapped[list["Progress"]] = relationship(  # type: ignore[name-defined]
        "Progress",
        back_populates="module",
        cascade="all, delete-orphan",
    )

    # many-to-many with Badge via ModuleBadge association table
    module_badges: Mapped[list["ModuleBadge"]] = relationship(  # type: ignore[name-defined]
        "ModuleBadge",
        back_populates="module",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<SkillModule id={self.id} title={self.title!r}>"
