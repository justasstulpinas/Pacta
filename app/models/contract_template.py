from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Boolean,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from sqlalchemy import Enum as SAEnum

from app.database import Base
from app.models.enums import TemplateStatus


# contractu template kurimas, (jeigu template istrinamas issitrina ir visi su ja sukurti failai)

class ContractTemplate(Base):
    __tablename__ = "contract_templates"
    _status_values = ",".join(f"'{status.value}'" for status in TemplateStatus)
    __table_args__ = (
        CheckConstraint(
            f"status IN ({_status_values})",
            name="ck_contract_templates_status",
        ),
    )


    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)

    content = Column(Text, nullable=False)

    status = Column(
    SAEnum(
        TemplateStatus,
        name="contract_template_status",
        native_enum=False,
        values_callable=lambda enum: [e.value for e in enum], 
        create_constraint=False,  
    ),
    nullable=False,
    default=TemplateStatus.DRAFT,
    index=True,
)

    logo_x = Column(Float, nullable=False, default=5.0)
    logo_y = Column(Float, nullable=False, default=5.0)
    logo_w = Column(Float, nullable=False, default=15.0)
    client_sig_x = Column(Float, nullable=True)
    client_sig_y = Column(Float, nullable=True)
    user_sig_x = Column(Float, nullable=True)
    user_sig_y = Column(Float, nullable=True)

    is_deleted = Column(Boolean, nullable=False, default=False, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.now(UTC))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
    )

    owner = relationship("User", back_populates="contract_templates")

    versions = relationship(
        "ContractTemplateVersion",
        back_populates="template",
        order_by="ContractTemplateVersion.version_number.desc()",
        cascade="all, delete-orphan",
    )


Index(
    "ix_contract_templates_owner_status",
    ContractTemplate.owner_id,
    ContractTemplate.status,
)
