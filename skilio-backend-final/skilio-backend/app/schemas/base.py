"""
app/schemas/base.py
───────────────────
Shared Pydantic configuration and base classes.

ORMBase: base class for all response schemas that need to read
         from SQLAlchemy ORM objects (model_config with from_attributes=True).

All response schemas should inherit from ORMBase.
All request/create schemas should inherit from plain BaseModel.
"""

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    """
    Base class for Pydantic schemas that are constructed from
    SQLAlchemy ORM model instances.

    model_config from_attributes=True is equivalent to Pydantic v1's
    orm_mode = True. It allows Pydantic to read values from ORM object
    attributes instead of requiring a plain dict.

    Example:
        user = db.query(User).first()    # SQLAlchemy ORM object
        UserResponse.model_validate(user) # works because from_attributes=True
    """

    model_config = ConfigDict(from_attributes=True)
