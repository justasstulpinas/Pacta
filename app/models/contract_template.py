from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Boolean,
    Enum,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Enum as SAEnum

from app.database import Base
from app.models.enums import ContractTemplateStatus



class ContractTemplate(Base):
    __tablename__ = "contract_templates"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','active','archived')",
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
        ContractTemplateStatus,
        name="contract_template_status",
        native_enum=False,
        values_callable=lambda enum: [e.value for e in enum], 
        create_constraint=False,  
    ),
    nullable=False,
    default=ContractTemplateStatus.DRAFT,
    index=True,
)

    is_deleted = Column(Boolean, nullable=False, default=False, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
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

