import logging
from datetime import datetime, UTC

from sqlalchemy.orm import Session

from app.models.enums import SubmissionStatus
from app.models.submission import Submission

logger = logging.getLogger(__name__)


def cleanup_expired_submissions(db: Session) -> int:
    """
    Mark PENDING submissions past their expires_at as EXPIRED and wipe any stored blobs.
    Audit trail rows are never deleted — they are retained permanently.
    Returns the number of submissions expired.
    """
    now = datetime.now(UTC)
    expired = (
        db.query(Submission)
        .filter(
            Submission.expires_at < now,
            Submission.status == SubmissionStatus.PENDING,
        )
        .all()
    )

    for sub in expired:
        sub.status = SubmissionStatus.EXPIRED
        sub.encrypted_pdf_blob = None
        sub.encryption_nonce = None
        sub.access_code_hash = ""
        sub.owner_download_code_hash = None

    if expired:
        db.commit()

    count = len(expired)
    if count:
        logger.info("cleanup: expired %d submission(s)", count)
    return count


def cleanup_signed_expired_blobs(db: Session) -> int:
    """
    For SIGNED submissions that have passed their expires_at without the owner downloading,
    wipe the encrypted blob but keep the audit trail and metadata.
    """
    now = datetime.now(UTC)
    stale = (
        db.query(Submission)
        .filter(
            Submission.expires_at < now,
            Submission.status == SubmissionStatus.SIGNED,
            Submission.encrypted_pdf_blob.isnot(None),
        )
        .all()
    )

    for sub in stale:
        sub.encrypted_pdf_blob = None
        sub.encryption_nonce = None
        sub.owner_download_code_hash = None
        sub.status = SubmissionStatus.EXPIRED

    if stale:
        db.commit()

    count = len(stale)
    if count:
        logger.info("cleanup: wiped blobs from %d stale signed submission(s)", count)
    return count
