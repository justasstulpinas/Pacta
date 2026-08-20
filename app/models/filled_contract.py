from datetime import datetime, UTC

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Text,
    String,
    CheckConstraint,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import SubmissionStatus

# Legacy submission table — submitted_data and rendered_content have been removed
# as part of the eIDAS GDPR compliance rewrite. No new rows should be written here;
# use app.models.submission.Submission for all new signing flows.
class FilledContract(Base):
    __tablename__ = "filled_contracts"
    _status_values = ",".join(f"'{status.value}'" for status in SubmissionStatus)

    id = Column(Integer, primary_key=True, index=True)

    template_id = Column(Integer, ForeignKey("contract_templates.id"), nullable=False)

    link_id = Column(Integer, ForeignKey("public_links.id"), nullable=False)

    submitted_at = Column(DateTime, default=datetime.now(UTC), nullable=False)

    signature_image = Column(Text, nullable=True)

    template_version = Column(Integer, nullable=True)

    template = relationship("ContractTemplate")

    ip_address = Column(String, nullable= False)

    user_agent = Column(String, nullable= True)

    submission_hash = Column(String,nullable= False)

    submitter_email = Column(String, nullable=True)

    status = Column(
        SAEnum(
            SubmissionStatus,
            name="filled_contract_status",
            native_enum=False,
            values_callable=lambda enum: [e.value for e in enum],
            create_constraint=False,
        ),
        nullable=False,
        default=SubmissionStatus.SUBMITTED,
    )

    confirmed_at = Column(DateTime, nullable=True)

    template_version_id = Column(
        Integer,
        ForeignKey("contract_template_versions.id"),
        nullable=True,
    )

    template_version_ref = relationship("ContractTemplateVersion")

    __table_args__ = (
        CheckConstraint(
            f"status IN ({_status_values})",
            name="filled_contract_status_check",
        ),
    )
