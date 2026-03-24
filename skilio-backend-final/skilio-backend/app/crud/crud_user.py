"""
app/crud/crud_user.py
─────────────────────
User-specific CRUD operations, extending the generic CRUDBase.

The auth service calls these functions — keeping DB queries out of the
service layer and making them independently testable.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Look up a user by email address. Case-insensitive."""
        return (
            db.query(User)
            .filter(User.email == email.lower())
            .first()
        )

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Override base create to handle password hashing.
        The generic CRUDBase.create() would try to set 'password' directly,
        but the User model stores 'hashed_password' — we need to intercept.
        """
        db_obj = User(
            email=obj_in.email.lower(),
            full_name=obj_in.full_name.strip(),
            hashed_password=hash_password(obj_in.password),
            is_active=True,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def deactivate(self, db: Session, *, user: User) -> User:
        """Soft-delete: set is_active=False instead of deleting the row."""
        user.is_active = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


# Module-level singleton — import this in services and routers:
#   from app.crud.crud_user import crud_user
crud_user = CRUDUser(User)
