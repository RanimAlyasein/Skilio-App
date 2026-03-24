"""
app/models/progress.py
───────────────────────
Progress model — one row per (child, module) pair.

Tracks how many lessons a child has completed in a module.
Updated by the progress_service after every scenario completion.

This is a materialized aggregate — it could be computed from
ScenarioAttempt records, but storing it here avoids expensive
re-aggregation on every dashboard load.
"""

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Progress(Base):
    __tablename__ = "progress"

    # Uniqueness enforced at the DB level:
    # a child can have only one Progress row per module
    __table_args__ = (
        UniqueConstraint("child_id", "module_id", name="uq_progress_child_module"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    child_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("children.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    module_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("skill_modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    lessons_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Cached total so we don't need to query lessons table on every dashboard load
    total_lessons: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamp of the most recent activity — used for "last active" display
    last_activity_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    child: Mapped["Child"] = relationship(  # type: ignore[name-defined]
        "Child",
        back_populates="progress_records",
    )

    module: Mapped["SkillModule"] = relationship(  # type: ignore[name-defined]
        "SkillModule",
        back_populates="progress_records",
    )

    @property
    def completion_percentage(self) -> float:
        """Convenience: percentage of lessons completed (0.0 – 100.0)."""
        if self.total_lessons == 0:
            return 0.0
        return round((self.lessons_completed / self.total_lessons) * 100, 1)

    def __repr__(self) -> str:
        return (
            f"<Progress child={self.child_id} module={self.module_id} "
            f"{self.lessons_completed}/{self.total_lessons}>"
        )
