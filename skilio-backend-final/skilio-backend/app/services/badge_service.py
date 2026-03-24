"""
app/services/badge_service.py
──────────────────────────────
Badge evaluation engine.

check_and_award_badges() is called after every scenario completion.
It evaluates all active badge trigger rules against the child's current
stats and creates BadgeAward records for any newly qualifying badges.

Returns only the *newly* awarded badges (not all badges the child holds)
so the frontend can show the "You earned a badge!" celebration.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.badge import Badge, BadgeAward, BadgeTriggerType
from app.models.child import Child
from app.models.lesson import Lesson
from app.models.scenario import AttemptStatus, ScenarioAttempt, ScenarioAttemptChoice, ScenarioChoice


def check_and_award_badges(
    db: Session,
    *,
    child_id: int,
) -> list[BadgeAward]:
    """
    Evaluate all active badge triggers for a child.
    Returns a list of BadgeAward records created during this call.
    """
    # Load the child (needed for XP checks)
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        return []

    # All active badges not yet earned by this child
    already_earned_ids = (
        db.query(BadgeAward.badge_id)
        .filter(BadgeAward.child_id == child_id)
        .subquery()
    )

    candidates = (
        db.query(Badge)
        .filter(
            Badge.is_active == True,  # noqa: E712
            Badge.id.not_in(already_earned_ids),
        )
        .all()
    )

    if not candidates:
        return []

    # Compute child stats once (avoid repeating queries per badge)
    stats = _compute_child_stats(db, child_id=child_id)

    new_awards: list[BadgeAward] = []

    for badge in candidates:
        if _qualifies(badge, child, stats):
            award = BadgeAward(
                child_id=child_id,
                badge_id=badge.id,
                trigger_context={
                    "trigger_type": badge.trigger_type.value,
                    "trigger_value": badge.trigger_value,
                    "child_xp_at_award": child.total_xp,
                },
            )
            db.add(award)

            # Award bonus XP for earning the badge
            if badge.xp_bonus > 0:
                child.total_xp = (child.total_xp or 0) + badge.xp_bonus
                db.add(child)

            new_awards.append(award)

    if new_awards:
        db.commit()
        for award in new_awards:
            db.refresh(award)

    return new_awards


def get_badges_for_child(db: Session, *, child_id: int) -> list[BadgeAward]:
    """All badges a child has earned, with badge data eagerly loaded."""
    from sqlalchemy.orm import joinedload
    return (
        db.query(BadgeAward)
        .options(joinedload(BadgeAward.badge))
        .filter(BadgeAward.child_id == child_id)
        .order_by(BadgeAward.awarded_at.desc())
        .all()
    )


# ── Private helpers ───────────────────────────────────────────────────────────

def _compute_child_stats(db: Session, *, child_id: int) -> dict:
    """
    Compute the stats needed to evaluate all badge trigger types.
    Called once per check_and_award_badges() invocation.
    """
    # Total completed attempts
    total_completed = (
        db.query(func.count(ScenarioAttempt.id))
        .filter(
            ScenarioAttempt.child_id == child_id,
            ScenarioAttempt.status == AttemptStatus.COMPLETED,
        )
        .scalar()
    ) or 0

    # Distinct lessons completed
    distinct_lessons_completed = (
        db.query(func.count(func.distinct(ScenarioAttempt.lesson_id)))
        .filter(
            ScenarioAttempt.child_id == child_id,
            ScenarioAttempt.status == AttemptStatus.COMPLETED,
        )
        .scalar()
    ) or 0

    # Total safe choices made (across all attempts)
    total_safe_choices = (
        db.query(func.count(ScenarioAttemptChoice.id))
        .join(ScenarioChoice, ScenarioChoice.id == ScenarioAttemptChoice.choice_id)
        .join(ScenarioAttempt, ScenarioAttempt.id == ScenarioAttemptChoice.attempt_id)
        .filter(
            ScenarioAttempt.child_id == child_id,
            ScenarioChoice.is_safe_choice == True,  # noqa: E712
        )
        .scalar()
    ) or 0

    # Modules fully completed
    from app.models.progress import Progress
    fully_completed_modules = (
        db.query(func.count(Progress.id))
        .filter(
            Progress.child_id == child_id,
            Progress.total_lessons > 0,
            Progress.lessons_completed >= Progress.total_lessons,
        )
        .scalar()
    ) or 0

    return {
        "total_completed_attempts": total_completed,
        "distinct_lessons_completed": distinct_lessons_completed,
        "total_safe_choices": total_safe_choices,
        "fully_completed_modules": fully_completed_modules,
    }


def _qualifies(badge: Badge, child: Child, stats: dict) -> bool:
    """Return True if the child now meets this badge's trigger condition."""
    t = badge.trigger_type
    v = badge.trigger_value

    if t == BadgeTriggerType.FIRST_LESSON:
        return stats["distinct_lessons_completed"] >= 1

    if t == BadgeTriggerType.LESSON_COUNT:
        return stats["distinct_lessons_completed"] >= v

    if t == BadgeTriggerType.MODULE_COMPLETE:
        return stats["fully_completed_modules"] >= v

    if t == BadgeTriggerType.XP_MILESTONE:
        return (child.total_xp or 0) >= v

    if t == BadgeTriggerType.SAFE_CHOICES:
        return stats["total_safe_choices"] >= v

    return False
