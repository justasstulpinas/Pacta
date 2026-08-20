from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

# varototjo profilio duomabze
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    profile_name = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    phone_number = Column(String(64), nullable=True)
    company_code = Column(String(64), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    signature_image = Column(Text, nullable=True)
    logo_image = Column(Text, nullable=True)
    logo_x = Column(Float, nullable=False, default=5.0)
    logo_y = Column(Float, nullable=False, default=5.0)
    created_at = Column(DateTime, nullable=False, default=datetime.now(UTC))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
    )

    user = relationship("User", back_populates="profile")
