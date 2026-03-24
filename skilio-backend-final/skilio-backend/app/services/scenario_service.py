"""
app/services/scenario_service.py
──────────────────────────────────
The scenario engine — the technical centrepiece of Skilio.

This service manages the full lifecycle of a scenario play-through:
  1. start_attempt()   — create a new attempt at a lesson's entry node
  2. advance_choice()  — submit a choice, move to next node, detect completion
  3. get_attempt()     — resume an in-progress attempt

On completion, it calls:
  - _award_xp()         — adds XP to the child's total
  - progress_service.update_progress() — updates the Progress table
  - badge_service.check_and_award_badges() — evaluates and awards any new badges

All HTTP concerns (status codes, HTTPException) are kept at the router layer.
This service raises plain Python ValueError / PermissionError for invalid states,
which the router converts to appropriate HTTP responses.
"""

from sqlalchemy.orm import Session

from app import crud
from app.crud import crud_scenario as db_scenario
from app.crud.crud_child import crud_child
from app.models.scenario import AttemptStatus, ScenarioAttempt
from app.schemas.scenario import AttemptWithNodeResponse, ChoiceResult


def start_attempt(
    db: Session,
    *,
    child_id: int,
    lesson_id: int,
    parent_id: int,
) -> ScenarioAttempt:
    """
    Start a new scenario attempt for a child.

    Steps:
      1. Verify the child belongs to this parent (ownership check)
      2. Check if an in-progress attempt already exists — if so, resume it
      3. Verify the lesson exists and has an entry node
      4. Create the ScenarioAttempt at the entry node

    Returns the attempt object. The router fetches the current node separately.
    """
    # 1. Ownership check
    from app.services.child_service import get_owned_child_or_404
    child = get_owned_child_or_404(db, child_id=child_id, parent_id=parent_id)

    # 2. Resume check
    existing = db_scenario.get_in_progress_attempt(db, child_id, lesson_id)
    if existing:
        return existing

    # 3. Lesson validation
    from app.models.lesson import Lesson
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise ValueError(f"Lesson {lesson_id} not found")
    if not lesson.entry_node_id:
        raise ValueError(f"Lesson {lesson_id} has no entry node — content not ready")

    # 4. Create attempt
    attempt = db_scenario.create_attempt(
        db,
        child_id=child_id,
        lesson_id=lesson_id,
        entry_node_id=lesson.entry_node_id,
    )
    return attempt


def advance_choice(
    db: Session,
    *,
    attempt_id: int,
    choice_id: int,
    parent_id: int,
) -> ChoiceResult:
    """
    Submit a choice during a scenario play-through.

    Steps:
      1. Load the attempt and verify ownership (parent owns the child)
      2. Verify the attempt is still in-progress
      3. Verify the choice belongs to the current node (prevents cheating)
      4. Record the choice in ScenarioAttemptChoice
      5a. If choice.next_node_id is None → complete the attempt
      5b. Otherwise → advance current_node_id to next_node_id
      6. On completion: award XP, update progress, check badges

    Returns ChoiceResult with the next node (or None on completion) and
    any newly awarded badge IDs for the frontend celebration screen.
    """
    # 1. Load + ownership check
    attempt = db_scenario.get_attempt(db, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")

    from app.services.child_service import get_owned_child_or_404
    child = get_owned_child_or_404(db, child_id=attempt.child_id, parent_id=parent_id)

    # 2. Status check
    if attempt.status != AttemptStatus.IN_PROGRESS:
        raise ValueError(
            f"Attempt is already {attempt.status.value} — cannot advance"
        )

    # 3. Validate choice belongs to current node
    choice = db_scenario.get_choice(db, choice_id)
    if not choice:
        raise ValueError("Choice not found")
    if not db_scenario.choice_belongs_to_node(choice, attempt.current_node_id):
        raise ValueError(
            "Choice does not belong to the current node — invalid submission"
        )

    # 4. Record the choice (audit trail)
    db_scenario.record_choice(
        db,
        attempt_id=attempt_id,
        node_id=attempt.current_node_id,
        choice_id=choice_id,
    )

    newly_awarded_badge_ids: list[int] = []

    # 5a. Completion path — no next node
    if choice.next_node_id is None:
        from app.models.lesson import Lesson
        lesson = db.query(Lesson).filter(Lesson.id == attempt.lesson_id).first()
        xp_to_award = lesson.xp_reward if lesson else 50

        # Partial XP for unsafe/wrong path
        if not choice.is_safe_choice:
            xp_to_award = max(10, xp_to_award // 5)

        attempt = db_scenario.complete_attempt(db, attempt=attempt, xp_earned=xp_to_award)

        # Award XP to child total
        _award_xp_to_child(db, child=child, xp=xp_to_award)

        # Update progress aggregate
        try:
            from app.services.progress_service import update_progress
            update_progress(db, child_id=child.id, module_id=lesson.module_id if lesson else None)
        except Exception:
            pass  # Progress update failure should not break the attempt

        # Check badges
        try:
            from app.services.badge_service import check_and_award_badges
            new_awards = check_and_award_badges(db, child_id=child.id)
            newly_awarded_badge_ids = [a.badge_id for a in new_awards]
        except Exception:
            pass  # Badge failure should not break the attempt

        return ChoiceResult(
            attempt=attempt,
            next_node=None,
            feedback=choice.feedback_text,
            newly_awarded_badge_ids=newly_awarded_badge_ids,
        )

    # 5b. Advance to next node
    attempt = db_scenario.advance_attempt_to_node(
        db,
        attempt=attempt,
        next_node_id=choice.next_node_id,
    )

    next_node = db_scenario.get_node_with_choices(db, choice.next_node_id)

    return ChoiceResult(
        attempt=attempt,
        next_node=next_node,
        feedback=choice.feedback_text,
        newly_awarded_badge_ids=[],
    )


def get_attempt_state(
    db: Session,
    *,
    attempt_id: int,
    parent_id: int,
) -> ScenarioAttempt:
    """
    Resume an attempt — returns current state including current node.
    Used when a child returns to a lesson mid-play-through.
    """
    attempt = db_scenario.get_attempt_with_node(db, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")

    from app.services.child_service import get_owned_child_or_404
    get_owned_child_or_404(db, child_id=attempt.child_id, parent_id=parent_id)

    return attempt


# ── Private helpers ───────────────────────────────────────────────────────────

def _award_xp_to_child(db: Session, *, child, xp: int) -> None:
    """Add XP to a child's running total."""
    crud_child.add_xp(db, child=child, xp=xp)
