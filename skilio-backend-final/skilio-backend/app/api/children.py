"""
app/api/children.py
────────────────────
Child management routes — all scoped to the authenticated parent.

GET    /api/children/              — list own children
POST   /api/children/              — create child
GET    /api/children/{id}          — get child detail
PUT    /api/children/{id}          — update child
DELETE /api/children/{id}          — soft-delete child
GET    /api/children/{id}/progress — module progress breakdown
GET    /api/children/{id}/badges   — earned badges
GET    /api/children/{id}/attempts — attempt history
GET    /api/children/{id}/summary  — dashboard summary (progress + badges combined)

All routes that operate on a specific child use Depends(get_owned_child),
which enforces the ownership check before the handler runs.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_owned_child, require_active_user
from app.schemas.badge import BadgeAwardResponse, ChildDashboardResponse, ModuleProgressResponse, ProgressResponse
from app.schemas.child import ChildCreate, ChildResponse, ChildSummaryResponse, ChildUpdate
from app.schemas.scenario import AttemptResponse

router = APIRouter()


# ── List / Create ─────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=list[ChildSummaryResponse],
    summary="List all children for the authenticated parent",
)
def list_children(
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    from app.services.child_service import list_children as svc_list
    return svc_list(db, parent_id=current_user.id)


@router.post(
    "/",
    response_model=ChildResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a child profile",
)
def create_child(
    child_in: ChildCreate,
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new child profile under the authenticated parent.
    Pydantic validates age (4–17) and display_name (1–50 chars) automatically.
    """
    from app.services.child_service import create_child as svc_create
    return svc_create(db, child_in=child_in, parent_id=current_user.id)


# ── Single child (ownership-guarded) ─────────────────────────────────────────

@router.get(
    "/{child_id}",
    response_model=ChildResponse,
    summary="Get a child profile",
)
def get_child(child=Depends(get_owned_child)):
    """
    Returns the child profile.
    get_owned_child dependency handles ownership verification and 404.
    """
    return child


@router.put(
    "/{child_id}",
    response_model=ChildResponse,
    summary="Update a child profile",
)
def update_child(
    update_in: ChildUpdate,
    child=Depends(get_owned_child),
    db: Session = Depends(get_db),
):
    from app.services.child_service import update_child as svc_update
    return svc_update(db, child=child, update_in=update_in)


@router.delete(
    "/{child_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a child profile",
)
def delete_child(
    child=Depends(get_owned_child),
    db: Session = Depends(get_db),
):
    """
    Soft-deletes the child profile (sets is_active=False).
    Attempt history and progress records are preserved for audit purposes.
    """
    from app.services.child_service import delete_child as svc_delete
    svc_delete(db, child=child)


# ── Child sub-resources ───────────────────────────────────────────────────────

@router.get(
    "/{child_id}/progress",
    response_model=list[ProgressResponse],
    summary="Get module-by-module progress for a child",
)
def get_child_progress(
    child=Depends(get_owned_child),
    db: Session = Depends(get_db),
):
    from app.services.progress_service import get_progress_for_child
    return get_progress_for_child(db, child_id=child.id)


@router.get(
    "/{child_id}/badges",
    response_model=list[BadgeAwardResponse],
    summary="Get all badges earned by a child",
)
def get_child_badges(
    child=Depends(get_owned_child),
    db: Session = Depends(get_db),
):
    from app.services.badge_service import get_badges_for_child
    return get_badges_for_child(db, child_id=child.id)


@router.get(
    "/{child_id}/attempts",
    response_model=list[AttemptResponse],
    summary="Get recent scenario attempts for a child",
)
def get_child_attempts(
    child=Depends(get_owned_child),
    db: Session = Depends(get_db),
):
    from app.crud.crud_scenario import get_attempts_for_child
    return get_attempts_for_child(db, child_id=child.id)


@router.get(
    "/{child_id}/summary",
    response_model=ChildDashboardResponse,
    summary="Get full dashboard summary for a child (progress + badges)",
)
def get_child_summary(
    child=Depends(get_owned_child),
    db: Session = Depends(get_db),
):
    """
    Returns everything the parent dashboard needs for a child detail page
    in a single request: progress per module, earned badges, and XP.
    """
    from app.crud.crud_scenario import get_attempts_for_child
    from app.services.badge_service import get_badges_for_child
    from app.services.progress_service import get_progress_for_child

    progress_records = get_progress_for_child(db, child_id=child.id)
    badge_awards = get_badges_for_child(db, child_id=child.id)
    recent_attempts = get_attempts_for_child(db, child_id=child.id, limit=5)

    module_progress = [
        ModuleProgressResponse(
            module_id=p.module_id,
            module_title=p.module.title if p.module else f"Module {p.module_id}",
            lessons_completed=p.lessons_completed,
            total_lessons=p.total_lessons,
            completion_percentage=p.completion_percentage,
            last_activity_at=p.last_activity_at,
        )
        for p in progress_records
    ]

    return ChildDashboardResponse(
        child_id=child.id,
        display_name=child.display_name,
        age=child.age,
        avatar_url=child.avatar_url,
        total_xp=child.total_xp,
        module_progress=module_progress,
        badges_earned=badge_awards,
        recent_attempt_count=len(recent_attempts),
    )
