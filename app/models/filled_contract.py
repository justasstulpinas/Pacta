from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, JSON, DateTime, Text, String, CheckConstraint
from sqlalchemy.sql import func
from app.database import Base

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

    ip_address = Column(String, nullable= False)

    user_agent = Column(String, nullable= True)

    submission_hash = Column(String,nullable= False)

    status = Column(String, nullable=False, default="submitted")

    confirmed_at = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "status IN ('submitted','confirmed','completed','cancelled')",
            name="filled_contract_status_check"
            ),
            )
    