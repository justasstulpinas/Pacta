import secrets
from datetime import datetime, UTC
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import SubmissionStatus


class Submission(Base):
    __tablename__ = "submissions"

    # Public identifier — UUID4 only, never exposed as sequential integer
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    template_id         = Column(Integer, ForeignKey("contract_templates.id"), nullable=False)
    template_version_id = Column(Integer, ForeignKey("contract_template_versions.id"), nullable=True)
    creator_id          = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Set when owner sends email invitation; nullable when owner shares link manually
    recipient_email = Column(String, nullable=True)

    # True if the resolved template content contains any SENSITIVE_PLACEHOLDERS
    is_sensitive = Column(Boolean, default=False, nullable=False)

    # Resolved template content (owner prefill + sys fields already injected).
    # Contains no client data — only owner/system placeholder values.
    resolved_content = Column(String, nullable=True)

    # --- Access code for recipient (Argon2 hash only — plaintext never stored) ---
    access_code_hash         = Column(String, nullable=False)
    access_attempts          = Column(Integer, default=0, nullable=False)
    access_locked_until      = Column(DateTime, nullable=True)

    # --- Owner download code (Argon2 hash only — plaintext sent in notification email) ---
    owner_download_code_hash        = Column(String, nullable=True)
    owner_download_attempts         = Column(Integer, default=0, nullable=False)
    owner_download_locked_until     = Column(DateTime, nullable=True)

    # --- Encrypted PDF blob (AES-256-GCM) ---
    # The AES key is NEVER stored here; it is embedded in the owner's download URL only.
    encrypted_pdf_blob = Column(LargeBinary, nullable=True)
    encryption_nonce   = Column(LargeBinary, nullable=True)  # 12-byte GCM nonce

    # Signature image captured from client (base64 data URI stored for audit purposes only)
    signature_image = Column(String, nullable=True)

    # Signature positions copied from the link/template at submission creation time
    logo_x        = Column(String, nullable=True)
    logo_y        = Column(String, nullable=True)
    logo_w        = Column(String, nullable=True)
    client_sig_x  = Column(String, nullable=True)
    client_sig_y  = Column(String, nullable=True)
    user_sig_x    = Column(String, nullable=True)
    user_sig_y    = Column(String, nullable=True)

    status = Column(
        SAEnum(
            SubmissionStatus,
            name="submission_status_enum",
            native_enum=False,
            values_callable=lambda e: [x.value for x in e],
            create_constraint=False,
        ),
        nullable=False,
        default=SubmissionStatus.PENDING,
    )

    created_at    = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    expires_at    = Column(DateTime, nullable=False)
    signed_at     = Column(DateTime, nullable=True)
    downloaded_at = Column(DateTime, nullable=True)

    template         = relationship("ContractTemplate")
    template_version = relationship("ContractTemplateVersion")
    creator          = relationship("User")
    audit_trail      = relationship(
        "SigningAuditTrail",
        back_populates="submission",
        uselist=False,
        cascade="all, delete-orphan",
    )
