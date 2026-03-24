"""
app/services/progress_service.py
──────────────────────────────────
Progress tracking — keeps the Progress table up to date after
each scenario completion.

update_progress() is called by scenario_service after every completion.
It is intentionally forgiving — failures here should not break the scenario flow.
"""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.models.progress import Progress
from app.models.scenario import AttemptStatus, ScenarioAttempt


def update_progress(
    db: Session,
    *,
    child_id: int,
    module_id: Optional[int],
) -> Optional[Progress]:
    """
    Recalculate and persist the Progress row for (child, module).
    Called after every scenario attempt completion.

    Algorithm:
      1. Count total published lessons in the module
      2. Count distinct lessons this child has at least one completed attempt for
      3. Upsert the Progress row
    """
    if module_id is None:
        return None

    # Total lessons in the module
    total = (
        db.query(func.count(Lesson.id))
        .filter(Lesson.module_id == module_id)
        .scalar()
    ) or 0

    # Distinct lessons the child has completed (at least once)
    completed_lesson_ids = (
        db.query(ScenarioAttempt.lesson_id)
        .join(Lesson, Lesson.id == ScenarioAttempt.lesson_id)
        .filter(
            ScenarioAttempt.child_id == child_id,
            ScenarioAttempt.status == AttemptStatus.COMPLETED,
            Lesson.module_id == module_id,
        )
        .distinct()
        .all()
    )
    completed_count = len(completed_lesson_ids)

    # Upsert the Progress row
    progress = (
        db.query(Progress)
        .filter(Progress.child_id == child_id, Progress.module_id == module_id)
        .first()
    )

    if progress is None:
        progress = Progress(
            child_id=child_id,
            module_id=module_id,
            lessons_completed=completed_count,
            total_lessons=total,
        )
        db.add(progress)
    else:
        progress.lessons_completed = completed_count
        progress.total_lessons = total
        db.add(progress)

    db.commit()
    db.refresh(progress)
    return progress


def get_progress_for_child(
    db: Session,
    *,
    child_id: int,
) -> list[Progress]:
    """All progress rows for a child, with module eagerly loaded."""
    from sqlalchemy.orm import joinedload
    return (
        db.query(Progress)
        .options(joinedload(Progress.module))
        .filter(Progress.child_id == child_id)
        .order_by(Progress.last_activity_at.desc())
        .all()
    )
