import uuid

from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base
# modelis sugeneruojantis public linko duomabze
class PublicLink(Base):
    __tablename__ = "public_links"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("contract_templates.id"), nullable=False)
    token = Column(String, unique=True, index= True, nullable=False)
    expires_at = Column(DateTime, nullable= False)
    is_revoked = Column(Boolean, default= False, nullable=False)
    resolved_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(UTC), nullable= False)
    template = relationship("ContractTemplate")
