"""
app/api/badges.py
──────────────────
Badge catalogue routes — read-only, accessible by any authenticated user.

GET /api/badges/     — list all active badges
GET /api/badges/{id} — single badge detail
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_active_user
from app.models.badge import Badge
from app.schemas.badge import BadgeResponse

router = APIRouter()


@router.get(
    "/",
    response_model=list[BadgeResponse],
    summary="List all available badges",
)
def list_badges(
    _=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """
    Returns all active badges in the platform.
    Used on the badge collection page to show locked/unlocked state.
    """
    return (
        db.query(Badge)
        .filter(Badge.is_active == True)  # noqa: E712
        .order_by(Badge.id)
        .all()
    )


@router.get(
    "/{badge_id}",
    response_model=BadgeResponse,
    summary="Get badge detail",
)
def get_badge(
    badge_id: int,
    _=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found",
        )
    return badge
