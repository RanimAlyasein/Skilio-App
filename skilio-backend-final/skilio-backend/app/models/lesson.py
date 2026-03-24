"""
app/models/lesson.py
─────────────────────
Lesson ORM model — a single learning unit inside a SkillModule.

⚠️  CIRCULAR FK NOTE:
Lesson.entry_node_id references scenario_nodes.id
ScenarioNode.lesson_id references lessons.id

Both tables reference each other. MySQL will refuse to create either table
first without the other existing. The solution:

1. entry_node_id uses use_alter=True — SQLAlchemy creates the column WITHOUT
   the FK constraint initially, then adds the constraint in a second ALTER TABLE
   after both tables exist.

2. In Alembic migrations, this generates the expected two-step SQL:
   - CREATE TABLE lessons (..., entry_node_id INT)   -- no FK yet
   - CREATE TABLE scenario_nodes (...)
   - ALTER TABLE lessons ADD CONSTRAINT fk_entry_node
       FOREIGN KEY (entry_node_id) REFERENCES scenario_nodes(id)

Relationships:
  Lesson  →  SkillModule     (many-to-one)
  Lesson  →  ScenarioNode    (entry_node — many-to-one, nullable)
  Lesson  →  ScenarioAttempt (one-to-many)
"""

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Lesson(Base, TimestampMixin):
    __tablename__ = "lessons"

    # ── Primary key ───────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── Foreign keys ──────────────────────────────────────────────────────────
    module_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("skill_modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Circular FK — use_alter defers the constraint to post-CREATE ALTER TABLE
    entry_node_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "scenario_nodes.id",
            use_alter=True,          # ← critical: prevents circular CREATE deadlock
            name="fk_lesson_entry_node",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    # ── Fields ────────────────────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(150), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=True)

    # XP awarded to child on scenario completion
    xp_reward: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    # Controls display order within the module
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ── Relationships ─────────────────────────────────────────────────────────
    module: Mapped["SkillModule"] = relationship(  # type: ignore[name-defined]
        "SkillModule",
        back_populates="lessons",
    )

    entry_node: Mapped["ScenarioNode | None"] = relationship(  # type: ignore[name-defined]
        "ScenarioNode",
        foreign_keys=[entry_node_id],
        post_update=True,   # required alongside use_alter to avoid FK ordering issues
    )

    # All nodes that belong to this lesson (not just the entry)
    nodes: Mapped[list["ScenarioNode"]] = relationship(  # type: ignore[name-defined]
        "ScenarioNode",
        foreign_keys="ScenarioNode.lesson_id",
        back_populates="lesson",
        cascade="all, delete-orphan",
    )

    attempts: Mapped[list["ScenarioAttempt"]] = relationship(  # type: ignore[name-defined]
        "ScenarioAttempt",
        back_populates="lesson",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Lesson id={self.id} title={self.title!r} module_id={self.module_id}>"
