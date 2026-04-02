from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

# contractu template versijos sekimas

class ContractTemplateVersion(Base):
    __tablename__ = "contract_template_versions"

    id = Column(Integer, primary_key=True, index=True)
    
    template_id = Column(Integer, ForeignKey("contract_templates.id"), nullable=False)

    version_number = Column(Integer, nullable=False)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    template = relationship("ContractTemplate", back_populates="versions")