"""
app/crud/base.py
────────────────
Generic CRUD base class.

Provides reusable get / get_multi / create / update / delete operations
for any SQLAlchemy model. Domain-specific CRUD modules inherit from this
and add their own query methods on top.

Usage:
    class CRUDChild(CRUDBase[Child, ChildCreate, ChildUpdate]):
        def get_by_parent(self, db, parent_id):
            return db.query(Child).filter(Child.parent_id == parent_id).all()

    crud_child = CRUDChild(Child)

This pattern keeps repetitive DB code out of service and router layers.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import Base

# Generic type variables
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD operations for a SQLAlchemy model.

    Type parameters:
        ModelType        — the SQLAlchemy ORM model class
        CreateSchemaType — the Pydantic schema used for creation
        UpdateSchemaType — the Pydantic schema used for updates
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Fetch a single record by primary key. Returns None if not found."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """
        Fetch a paginated list of records.
        skip/limit implement offset pagination.
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record from a Pydantic create schema.
        Commits and refreshes the object so server_defaults are populated.
        """
        obj_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Update an existing record.

        Accepts either a Pydantic update schema or a plain dict.
        Only fields explicitly set in obj_in are updated (PATCH semantics).
        Fields not present in obj_in are left unchanged.
        """
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # exclude_unset=True is crucial: it means only fields the client
            # actually sent are included — None values won't overwrite existing data
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        """
        Delete a record by primary key.
        Returns the deleted object (useful for confirmation responses).
        Returns None if the record didn't exist.
        """
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
