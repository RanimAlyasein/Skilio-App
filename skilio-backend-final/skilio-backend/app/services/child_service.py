"""
app/services/child_service.py
──────────────────────────────
Child domain business logic.

The get_owned_child() function here is what the FastAPI dependency
in dependencies.py delegates to — centralising the ownership check.
"""

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_child import crud_child
from app.models.child import Child
from app.schemas.child import ChildCreate, ChildUpdate


def get_owned_child_or_404(
    db: Session,
    *,
    child_id: int,
    parent_id: int,
) -> Child:
    """
    Fetch a child by ID, verified to belong to parent_id.
    Raises HTTP 404 for both "not found" and "wrong owner" cases —
    we intentionally do not distinguish them to prevent resource enumeration.
    """
    child = crud_child.get_owned(db, child_id=child_id, parent_id=parent_id)
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found",
        )
    return child


def list_children(db: Session, *, parent_id: int) -> list[Child]:
    return crud_child.get_by_parent(db, parent_id=parent_id)


def create_child(db: Session, *, child_in: ChildCreate, parent_id: int) -> Child:
    return crud_child.create_for_parent(db, obj_in=child_in, parent_id=parent_id)


def update_child(
    db: Session,
    *,
    child: Child,
    update_in: ChildUpdate,
) -> Child:
    return crud_child.update(db, db_obj=child, obj_in=update_in)


def delete_child(db: Session, *, child: Child) -> None:
    """Soft-delete: preserves the child's attempt history for parent records."""
    crud_child.soft_delete(db, child=child)
