"""
app/models/scenario.py
───────────────────────
The scenario engine models — the technical centrepiece of Skilio.

Four models:

  ScenarioNode
    A single story beat. Has content text, optional image, and a node_type.
    Connected to a Lesson and to multiple ScenarioChoices.

  ScenarioChoice
    One option at a ScenarioNode. Points to next_node_id (another ScenarioNode).
    next_node_id=NULL means this choice ends the scenario.

    This creates a SELF-REFERENTIAL DIRECTED GRAPH:
    ScenarioNode ──► ScenarioChoice ──► ScenarioNode (next)
                                    └──► NULL (end)

  ScenarioAttempt
    One play-through of a Lesson by a Child.
    Tracks the current node, status, XP earned, and timestamps.

  ScenarioAttemptChoice
    Junction / audit log: records every individual choice made during an attempt.
    Allows parents to replay exactly what path their child took.
"""

import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


# ── Enumerations ──────────────────────────────────────────────────────────────

class NodeType(str, enum.Enum):
    START  = "start"   # entry point of a scenario (each lesson has exactly one)
    BRANCH = "branch"  # middle node with choices leading onward
    END    = "end"     # terminal node (no further choices; scenario is over)


class AttemptStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"  # child is actively playing
    COMPLETED   = "completed"    # child reached an END node
    ABANDONED   = "abandoned"    # child left mid-scenario (timeout or manual exit)


# ── ScenarioNode ──────────────────────────────────────────────────────────────

class ScenarioNode(Base, TimestampMixin):
    """
    A single beat in a branching story.

    Every node belongs to exactly one Lesson. The Lesson's entry_node_id
    points to the START node; the engine advances from there.
    """
    __tablename__ = "scenario_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    lesson_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content_text: Mapped[str] = mapped_column(Text, nullable=False)

    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    node_type: Mapped[NodeType] = mapped_column(
        Enum(NodeType),
        nullable=False,
        default=NodeType.BRANCH,
    )

    # True if navigating to this node represents the "correct" / safe path.
    # Used to award full XP vs partial XP on completion.
    is_correct_path: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ── Relationships ─────────────────────────────────────────────────────────
    lesson: Mapped["Lesson"] = relationship(  # type: ignore[name-defined]
        "Lesson",
        foreign_keys=[lesson_id],
        back_populates="nodes",
    )

    # Choices originating FROM this node
    choices: Mapped[list["ScenarioChoice"]] = relationship(
        "ScenarioChoice",
        foreign_keys="ScenarioChoice.node_id",
        back_populates="node",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ScenarioNode id={self.id} type={self.node_type.value} "
            f"lesson_id={self.lesson_id}>"
        )


# ── ScenarioChoice ────────────────────────────────────────────────────────────

class ScenarioChoice(Base):
    """
    One choosable option at a ScenarioNode.

    The self-referential FK (next_node_id → scenario_nodes.id) is what
    makes this a graph rather than a simple tree.

    next_node_id=NULL signals a terminal choice — the scenario ends
    when this choice is selected.
    """
    __tablename__ = "scenario_choices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # The node this choice belongs to (where the choice is presented)
    node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("scenario_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The node this choice leads to (NULL = end of scenario)
    # SELF-REFERENTIAL FK — same table, different semantic role
    next_node_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("scenario_nodes.id", ondelete="SET NULL"),
        nullable=True,
    )

    choice_text: Mapped[str] = mapped_column(String(500), nullable=False)

    # Whether this represents the safe / correct action
    is_safe_choice: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Short feedback shown after this choice is selected
    # e.g. "Great thinking! Telling a trusted adult is always the right move."
    feedback_text: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Display order among sibling choices at the same node
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ── Relationships ─────────────────────────────────────────────────────────
    node: Mapped["ScenarioNode"] = relationship(
        "ScenarioNode",
        foreign_keys=[node_id],
        back_populates="choices",
    )

    next_node: Mapped["ScenarioNode | None"] = relationship(
        "ScenarioNode",
        foreign_keys=[next_node_id],
    )

    def __repr__(self) -> str:
        return (
            f"<ScenarioChoice id={self.id} node_id={self.node_id} "
            f"→ next_node_id={self.next_node_id}>"
        )


# ── ScenarioAttempt ───────────────────────────────────────────────────────────

class ScenarioAttempt(Base, TimestampMixin):
    """
    One play-through of a Lesson by a Child.

    Tracks the child's current position in the node graph (current_node_id)
    and the overall status of the attempt.
    """
    __tablename__ = "scenario_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    child_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("children.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    lesson_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The node the child is currently at (updated on each choice)
    current_node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("scenario_nodes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    status: Mapped[AttemptStatus] = mapped_column(
        Enum(AttemptStatus),
        nullable=False,
        default=AttemptStatus.IN_PROGRESS,
    )

    xp_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    completed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    child: Mapped["Child"] = relationship(  # type: ignore[name-defined]
        "Child",
        back_populates="attempts",
    )

    lesson: Mapped["Lesson"] = relationship(  # type: ignore[name-defined]
        "Lesson",
        back_populates="attempts",
    )

    current_node: Mapped["ScenarioNode"] = relationship(
        "ScenarioNode",
        foreign_keys=[current_node_id],
    )

    # All individual choices recorded during this attempt
    attempt_choices: Mapped[list["ScenarioAttemptChoice"]] = relationship(
        "ScenarioAttemptChoice",
        back_populates="attempt",
        cascade="all, delete-orphan",
        order_by="ScenarioAttemptChoice.id",
    )

    def __repr__(self) -> str:
        return (
            f"<ScenarioAttempt id={self.id} child_id={self.child_id} "
            f"lesson_id={self.lesson_id} status={self.status.value}>"
        )


# ── ScenarioAttemptChoice ─────────────────────────────────────────────────────

class ScenarioAttemptChoice(Base):
    """
    Junction / audit table: one row per choice made during an attempt.

    Enables parents to see the exact path their child took through a scenario:
    which node they were at, which choice they made, and when.
    """
    __tablename__ = "scenario_attempt_choices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    attempt_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("scenario_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The node the child was at when they made this choice
    node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("scenario_nodes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # The choice they selected
    choice_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("scenario_choices.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Server-side timestamp — when the child made this choice
    from sqlalchemy import func
    chosen_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    attempt: Mapped["ScenarioAttempt"] = relationship(
        "ScenarioAttempt",
        back_populates="attempt_choices",
    )

    node: Mapped["ScenarioNode"] = relationship(
        "ScenarioNode",
        foreign_keys=[node_id],
    )

    choice: Mapped["ScenarioChoice"] = relationship(
        "ScenarioChoice",
        foreign_keys=[choice_id],
    )

    def __repr__(self) -> str:
        return (
            f"<ScenarioAttemptChoice attempt={self.attempt_id} "
            f"node={self.node_id} choice={self.choice_id}>"
        )
