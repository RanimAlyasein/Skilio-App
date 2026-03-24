"""
app/models/child.py
────────────────────
Child ORM model — represents a child profile owned by a parent User.

Relationships:
  Child  →  User          (many-to-one: each child has one parent)
  Child  →  ScenarioAttempt  (one-to-many: a child has many attempts)
  Child  →  BadgeAward    (one-to-many: a child earns many badges)
  Child  →  Progress      (one-to-many: a child has progress per module)
"""

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Child(Base, TimestampMixin):
    __tablename__ = "children"

    # ── Primary key ───────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── Ownership FK ──────────────────────────────────────────────────────────
    parent_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Fields ────────────────────────────────────────────────────────────────
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)

    age: Mapped[int] = mapped_column(Integer, nullable=False)

    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    total_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ── Relationships ─────────────────────────────────────────────────────────
    parent: Mapped["User"] = relationship("User", back_populates="children")  # type: ignore[name-defined]

    attempts: Mapped[list["ScenarioAttempt"]] = relationship(  # type: ignore[name-defined]
        "ScenarioAttempt",
        back_populates="child",
        cascade="all, delete-orphan",
    )

    badge_awards: Mapped[list["BadgeAward"]] = relationship(  # type: ignore[name-defined]
        "BadgeAward",
        back_populates="child",
        cascade="all, delete-orphan",
    )

    progress_records: Mapped[list["Progress"]] = relationship(  # type: ignore[name-defined]
        "Progress",
        back_populates="child",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Child id={self.id} name={self.display_name!r} parent_id={self.parent_id}>"
