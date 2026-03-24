"""
app/crud/crud_child.py
───────────────────────
Child-specific database operations.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.child import Child
from app.schemas.child import ChildCreate, ChildUpdate


class CRUDChild(CRUDBase[Child, ChildCreate, ChildUpdate]):

    def get_by_parent(self, db: Session, *, parent_id: int) -> list[Child]:
        """Return all active children belonging to a parent."""
        return (
            db.query(Child)
            .filter(Child.parent_id == parent_id, Child.is_active == True)  # noqa: E712
            .order_by(Child.created_at)
            .all()
        )

    def get_owned(
        self,
        db: Session,
        *,
        child_id: int,
        parent_id: int,
    ) -> Optional[Child]:
        """
        Fetch a child by ID only if it belongs to parent_id.
        Returns None if the child doesn't exist OR belongs to a different parent.
        This is the ownership-safe lookup used in the dependency guard.
        """
        return (
            db.query(Child)
            .filter(
                Child.id == child_id,
                Child.parent_id == parent_id,
                Child.is_active == True,  # noqa: E712
            )
            .first()
        )

    def create_for_parent(
        self,
        db: Session,
        *,
        obj_in: ChildCreate,
        parent_id: int,
    ) -> Child:
        """Create a child record linked to a specific parent."""
        child = Child(
            parent_id=parent_id,
            display_name=obj_in.display_name,
            age=obj_in.age,
            avatar_url=obj_in.avatar_url,
            total_xp=0,
            is_active=True,
        )
        db.add(child)
        db.commit()
        db.refresh(child)
        return child

    def add_xp(self, db: Session, *, child: Child, xp: int) -> Child:
        """Add XP to a child's total. Used by the scenario completion service."""
        child.total_xp = (child.total_xp or 0) + xp
        db.add(child)
        db.commit()
        db.refresh(child)
        return child

    def soft_delete(self, db: Session, *, child: Child) -> Child:
        """Deactivate instead of hard-deleting — preserves attempt history."""
        child.is_active = False
        db.add(child)
        db.commit()
        db.refresh(child)
        return child


crud_child = CRUDChild(Child)
