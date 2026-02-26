from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from app.database import Base

class FilledContract(Base):
    __tablename__ = "filled_contracts"

    id = Column(Integer, primary_key=True, index=True)

    template_id = Column(Integer, ForeignKey("contract_templates.id"), nullable=False)
    
    link_id = Column(Integer,ForeignKey("public_links.id"), nullable=False)

    submitted_data = Column(JSON, nullable=False)

    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    rendered_content = Column(Text, nullable=False)

    template = relationship("ContractTemplate")