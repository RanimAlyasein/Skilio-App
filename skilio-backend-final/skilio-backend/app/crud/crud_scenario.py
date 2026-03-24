"""
app/crud/crud_scenario.py
──────────────────────────
Database operations for the scenario engine.

Kept thin — just raw DB reads/writes.
All business logic (ownership checks, XP calculation, badge triggers)
lives in app/services/scenario_service.py.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.scenario import (
    AttemptStatus,
    ScenarioAttempt,
    ScenarioAttemptChoice,
    ScenarioChoice,
    ScenarioNode,
)


# ── ScenarioNode ──────────────────────────────────────────────────────────────

def get_node_with_choices(db: Session, node_id: int) -> Optional[ScenarioNode]:
    """
    Fetch a node and eagerly load its choices in one query.
    Avoids N+1 queries when the router returns node + choices together.
    """
    return (
        db.query(ScenarioNode)
        .options(joinedload(ScenarioNode.choices))
        .filter(ScenarioNode.id == node_id)
        .first()
    )


def get_nodes_for_lesson(db: Session, lesson_id: int) -> list[ScenarioNode]:
    """Return all nodes belonging to a lesson (used for admin/seed tooling)."""
    return (
        db.query(ScenarioNode)
        .filter(ScenarioNode.lesson_id == lesson_id)
        .all()
    )


# ── ScenarioAttempt ───────────────────────────────────────────────────────────

def get_attempt(db: Session, attempt_id: int) -> Optional[ScenarioAttempt]:
    return db.query(ScenarioAttempt).filter(ScenarioAttempt.id == attempt_id).first()


def get_attempt_with_node(db: Session, attempt_id: int) -> Optional[ScenarioAttempt]:
    """Fetch attempt and eagerly load current_node + its choices."""
    return (
        db.query(ScenarioAttempt)
        .options(
            joinedload(ScenarioAttempt.current_node).joinedload(ScenarioNode.choices)
        )
        .filter(ScenarioAttempt.id == attempt_id)
        .first()
    )


def get_attempts_for_child(
    db: Session,
    child_id: int,
    *,
    limit: int = 20,
) -> list[ScenarioAttempt]:
    """Recent attempts for a child — for parent history display."""
    return (
        db.query(ScenarioAttempt)
        .filter(ScenarioAttempt.child_id == child_id)
        .order_by(ScenarioAttempt.created_at.desc())
        .limit(limit)
        .all()
    )


def get_in_progress_attempt(
    db: Session,
    child_id: int,
    lesson_id: int,
) -> Optional[ScenarioAttempt]:
    """
    Check if a child already has an in-progress attempt for this lesson.
    Used to resume rather than creating a duplicate.
    """
    return (
        db.query(ScenarioAttempt)
        .filter(
            ScenarioAttempt.child_id == child_id,
            ScenarioAttempt.lesson_id == lesson_id,
            ScenarioAttempt.status == AttemptStatus.IN_PROGRESS,
        )
        .first()
    )


def create_attempt(
    db: Session,
    *,
    child_id: int,
    lesson_id: int,
    entry_node_id: int,
) -> ScenarioAttempt:
    attempt = ScenarioAttempt(
        child_id=child_id,
        lesson_id=lesson_id,
        current_node_id=entry_node_id,
        status=AttemptStatus.IN_PROGRESS,
        xp_earned=0,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def advance_attempt_to_node(
    db: Session,
    *,
    attempt: ScenarioAttempt,
    next_node_id: int,
) -> ScenarioAttempt:
    """Move current_node_id forward after a choice is made."""
    attempt.current_node_id = next_node_id
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def complete_attempt(
    db: Session,
    *,
    attempt: ScenarioAttempt,
    xp_earned: int,
) -> ScenarioAttempt:
    """Mark an attempt as completed and record XP."""
    attempt.status = AttemptStatus.COMPLETED
    attempt.xp_earned = xp_earned
    attempt.completed_at = datetime.now(timezone.utc)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


# ── ScenarioAttemptChoice ─────────────────────────────────────────────────────

def record_choice(
    db: Session,
    *,
    attempt_id: int,
    node_id: int,
    choice_id: int,
) -> ScenarioAttemptChoice:
    """
    Record a single choice made during an attempt.
    Called every time a child selects an option — builds the audit trail.
    """
    record = ScenarioAttemptChoice(
        attempt_id=attempt_id,
        node_id=node_id,
        choice_id=choice_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_attempt_choices(
    db: Session,
    attempt_id: int,
) -> list[ScenarioAttemptChoice]:
    """Full ordered choice trail for one attempt — for parent review."""
    return (
        db.query(ScenarioAttemptChoice)
        .options(
            joinedload(ScenarioAttemptChoice.node),
            joinedload(ScenarioAttemptChoice.choice),
        )
        .filter(ScenarioAttemptChoice.attempt_id == attempt_id)
        .order_by(ScenarioAttemptChoice.id)
        .all()
    )


# ── ScenarioChoice validation ─────────────────────────────────────────────────

def get_choice(db: Session, choice_id: int) -> Optional[ScenarioChoice]:
    return db.query(ScenarioChoice).filter(ScenarioChoice.id == choice_id).first()


def choice_belongs_to_node(choice: ScenarioChoice, node_id: int) -> bool:
    """
    Verify the submitted choice actually belongs to the current node.
    Prevents clients from submitting choices from other nodes in the scenario.
    """
    return choice.node_id == node_id
