import secrets
from datetime import datetime, UTC, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

from app.core.exceptions import BadRequestError

_ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=2,
)

MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


class CodeService:
    @staticmethod
    def generate() -> tuple[str, str]:
        """
        Generate a cryptographically secure 6-digit code.
        Returns (plaintext_code, argon2_hash).
        Only the hash should be persisted — never the plaintext.
        """
        code = f"{secrets.randbelow(1_000_000):06d}"
        hashed = _ph.hash(code)
        return code, hashed

    @staticmethod
    def verify(plaintext: str, stored_hash: str) -> bool:
        try:
            return _ph.verify(stored_hash, plaintext)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    @staticmethod
    def is_locked(locked_until: datetime | None) -> bool:
        if locked_until is None:
            return False
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=UTC)
        return datetime.now(UTC) < locked_until

    @staticmethod
    def next_locked_until(attempts: int) -> datetime | None:
        """Return lockout expiry if attempts has reached MAX_ATTEMPTS, else None."""
        if attempts >= MAX_ATTEMPTS:
            return datetime.now(UTC) + timedelta(minutes=LOCKOUT_MINUTES)
        return None
