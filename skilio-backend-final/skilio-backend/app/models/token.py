"""
app/models/token.py
────────────────────
RefreshToken model — stored refresh tokens for secure rotation.

Why store refresh tokens in the database?
- Allows individual token revocation (logout from one device)
- Allows "logout all devices" (delete all tokens for a user)
- Detects token reuse attacks (if a revoked token is presented again,
  it signals a stolen token — all user tokens can be wiped)

The token itself is NOT stored — only its SHA-256 hash.
This means a DB breach doesn't expose usable tokens.
"""

import hashlib

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    # Composite index for fast lookup by user + revoked status
    __table_args__ = (
        Index("ix_refresh_tokens_user_active", "user_id", "revoked"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # SHA-256 hash of the actual token string — never store the raw token
    token_hash: Mapped[str] = mapped_column(
        String(64),    # SHA-256 hex digest is always 64 chars
        nullable=False,
        unique=True,
        index=True,
    )

    expires_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User")  # type: ignore[name-defined]

    # ── Class methods ─────────────────────────────────────────────────────────
    @staticmethod
    def hash_token(raw_token: str) -> str:
        """Hash a raw token string for storage. SHA-256, hex-encoded."""
        return hashlib.sha256(raw_token.encode()).hexdigest()

    def __repr__(self) -> str:
        return (
            f"<RefreshToken user={self.user_id} "
            f"revoked={self.revoked} expires={self.expires_at}>"
        )
