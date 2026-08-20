from datetime import datetime, UTC

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class SigningAuditTrail(Base):
    """
    Immutable audit record created at the moment of signing.
    Never deleted — retained permanently for eIDAS compliance.
    Never contains personal IDs, rendered HTML, or verification codes.
    """
    __tablename__ = "signing_audit_trails"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    submission_uuid = Column(String(36), ForeignKey("submissions.uuid"), nullable=False, unique=True)

    # SHA-256 hash of the fully-rendered contract HTML (with all placeholders filled)
    # Stored so document integrity can be verified later without keeping the document.
    document_hash = Column(String(64), nullable=False)

    # Signer identity evidence
    recipient_email   = Column(String, nullable=True)
    recipient_ip      = Column(String, nullable=False)
    user_agent        = Column(String, nullable=True)
    browser_language  = Column(String, nullable=True)
    timezone          = Column(String, nullable=True)
    screen_resolution = Column(String, nullable=True)

    # Legal name entered by signer during the signing step
    signer_full_name = Column(String, nullable=False)

    # Explicit consent captured from mandatory checkboxes
    confirmed_read   = Column(Boolean, nullable=False)  # "I have read this contract"
    confirmed_esign  = Column(Boolean, nullable=False)  # "I agree to sign electronically"

    # Timestamps for the signing timeline
    code_verified_at   = Column(DateTime, nullable=False)  # when access code was verified
    contract_viewed_at = Column(DateTime, nullable=True)   # when client first loaded preview
    signed_at          = Column(DateTime, nullable=False)  # when sign button was submitted

    # Creator evidence
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator_ip = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    submission = relationship("Submission", back_populates="audit_trail")
    creator    = relationship("User")
