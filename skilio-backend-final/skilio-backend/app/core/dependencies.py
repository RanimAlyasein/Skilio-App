"""
app/core/dependencies.py
────────────────────────
FastAPI dependency functions injected via Depends().

Three categories:
  1. Database session      — get_db()
  2. Auth                  — get_current_user(), require_active_user()
  3. Ownership guards      — get_owned_child(), get_owned_attempt()

Ownership guards return HTTP 404 (not 403) for both "not found" and
"wrong owner" cases — returning 403 leaks that the resource exists.
"""

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token


# ── Database session ──────────────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    """
    Yield a SQLAlchemy session for the duration of a request.
    The finally block guarantees the session is closed even if an
    exception propagates — prevents connection pool exhaustion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Auth ──────────────────────────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Decode the JWT Bearer token and return the corresponding User.
    Raises HTTP 401 if token is missing, invalid, expired, or user deleted.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    from app.models.user import User
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


def require_active_user(current_user=Depends(get_current_user)):
    """
    Extends get_current_user — additionally blocks deactivated accounts.
    Use this on any route that should be inaccessible after account deactivation.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support.",
        )
    return current_user


# ── Ownership guards ──────────────────────────────────────────────────────────

def get_owned_child(
    child_id: int,
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """
    Fetch a Child by ID, verified to belong to current_user.
    Returns the Child ORM object on success.
    Raises HTTP 404 for both not-found and wrong-owner cases.

    Usage:
        @router.get("/children/{child_id}/progress")
        def get_progress(child=Depends(get_owned_child)):
            ...
    """
    from app.models.child import Child

    child = (
        db.query(Child)
        .filter(
            Child.id == child_id,
            Child.parent_id == current_user.id,
            Child.is_active == True,  # noqa: E712
        )
        .first()
    )

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )

    return child


def get_owned_attempt(
    attempt_id: int,
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """
    Fetch a ScenarioAttempt verified to belong to a child of current_user.
    Used on attempt detail and choice-submission routes.
    """
    from app.models.child import Child
    from app.models.scenario import ScenarioAttempt

    attempt = (
        db.query(ScenarioAttempt)
        .join(Child, Child.id == ScenarioAttempt.child_id)
        .filter(
            ScenarioAttempt.id == attempt_id,
            Child.parent_id == current_user.id,
        )
        .first()
    )

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )

    return attempt
