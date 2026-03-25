from sqlalchemy import Column, Integer, String, DateTime
from datetime import UTC, datetime

from app.database import Base

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key = True)
    jti = Column(String, unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    # sukuriama db revoked tokenams, kai user requestine logout, irasas isiraso i sita lentele, tokenas tampa negaliojanciu