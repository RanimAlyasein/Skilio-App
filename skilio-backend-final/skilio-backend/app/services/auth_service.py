"""
app/services/auth_service.py
─────────────────────────────
Authentication business logic.

This layer sits between the router (HTTP) and the database (CRUD).
It knows about business rules — but not about HTTP status codes or
request/response objects.

Functions here are pure Python and can be unit-tested without FastAPI.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Look up a user by email. Returns None if not found."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Look up a user by primary key. Returns None if not found."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a new User record.
    Hashes the password before persisting.
    Caller is responsible for checking that the email is not already taken.
    """
    user = User(
        email=user_in.email.lower(),  # normalise email to lowercase
        full_name=user_in.full_name.strip(),
        hashed_password=hash_password(user_in.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)  # reload from DB to populate server_defaults (created_at etc.)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Verify credentials.
    Returns the User if valid, None otherwise.
    Always calls verify_password (even if user not found) to prevent
    timing-based user enumeration attacks.
    """
    user = get_user_by_email(db, email.lower())

    # Always run verify_password to maintain constant-time behaviour.
    # If user is None, we hash against a dummy string to burn the same time.
    dummy_hash = "$2b$12$KIXAnbG5T3oRQF9K4tG9BuKFk3/T8I4k3Rl3e1R9v5Y0Y3Hg8YYWC"
    stored_hash = user.hashed_password if user else dummy_hash

    if not verify_password(password, stored_hash):
        return None

    if user is None:
        return None

    return user
