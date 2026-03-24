"""
app/api/users.py
─────────────────
User account routes — for the authenticated parent to manage their own profile.

GET  /api/users/me       — read own profile (duplicate of /auth/me, kept for REST symmetry)
PUT  /api/users/me       — update own profile (name only — email change is out of scope)
DELETE /api/users/me     — deactivate own account (soft delete)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_active_user
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
def get_me(current_user=Depends(require_active_user)):
    """Return the authenticated parent's profile."""
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
def update_me(
    update_in: UserUpdate,
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """
    Update the authenticated parent's profile.
    Only full_name is updatable — email changes require a separate
    verified flow (out of scope for MVP).
    """
    if update_in.full_name is not None:
        current_user.full_name = update_in.full_name.strip()
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
    return current_user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate own account",
)
def deactivate_me(
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """
    Soft-delete the authenticated parent's account.
    Sets is_active=False — data is retained for record-keeping.
    The JWT will still decode successfully, but require_active_user
    will reject subsequent requests with 403.
    """
    current_user.is_active = False
    db.add(current_user)
    db.commit()
