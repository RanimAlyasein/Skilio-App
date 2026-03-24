"""
app/models/base.py
──────────────────
Shared SQLAlchemy mixins and base utilities used by all ORM models.

TimestampMixin: adds created_at and updated_at columns to any model.
    class User(Base, TimestampMixin):
        ...

This avoids duplicating the same two columns across every model.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """
    Adds database-managed created_at and updated_at columns.

    - created_at: set once by the DB on INSERT (server_default)
    - updated_at: updated automatically by the DB on every UPDATE (onupdate)

    Using server_default / onupdate keeps timestamps accurate even if rows
    are modified directly in MySQL (bypassing the ORM).
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
