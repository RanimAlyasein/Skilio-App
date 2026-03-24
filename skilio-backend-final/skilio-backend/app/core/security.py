"""
app/core/security.py
────────────────────
All cryptographic operations live here:
  - Password hashing / verification (bcrypt via passlib)
  - JWT access token creation
  - JWT token decoding / verification

Nothing in this module touches the database or HTTP layer.
It is pure utility — importable and testable in isolation.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

# ── Password hashing ──────────────────────────────────────────────────────────
# bcrypt is intentionally slow, which is what you want for passwords.
# deprecated="auto" ensures old hashes are flagged for rehashing.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password. Store the result — never the original."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored hash.
    Returns True if they match, False otherwise.
    Timing-safe — does not leak information via timing attacks.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT tokens ────────────────────────────────────────────────────────────────

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: Typically the user's email or user ID (stored in 'sub' claim).
        expires_delta: Custom expiry. Falls back to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        Signed JWT string.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": subject,          # subject (user identifier)
        "exp": expire,           # expiry timestamp
        "iat": datetime.now(timezone.utc),  # issued-at
        "type": "access",        # token type guard
    }

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT refresh token with a longer expiry.
    The 'type' claim differentiates it from access tokens —
    the server should reject a refresh token used as an access token.
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.refresh_token_expire_days)

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Returns the payload dict on success.
    Raises JWTError if the token is invalid, expired, or tampered with.
    Callers should catch JWTError and convert to HTTP 401.
    """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


def decode_access_token(token: str) -> Optional[str]:
    """
    Convenience wrapper: decode an access token and return the subject (email).
    Returns None if decoding fails or token is not an access token.
    Use this in get_current_user dependency.
    """
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return payload.get("sub")
    except JWTError:
        return None
