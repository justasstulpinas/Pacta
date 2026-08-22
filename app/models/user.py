from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.user_roles import user_roles


# user buombaze kurioje susijungia user duomenys, su userio surinktais kontaktais, sutartimis ir profiliu
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean,default=False, nullable=False)
    verification_token = Column(String, nullable=True)
    last_login = Column(DateTime, nullable=True)
    is_suspended = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=True)
    failed_login_attempts: int = Column(Integer, default=0, nullable=False)
    locked_until: datetime | None = Column(DateTime(timezone=True), nullable=True)


    roles = relationship(
        "Role",
        secondary=user_roles,     
        lazy="selectin",
    )

    contract_templates = relationship(
        "ContractTemplate",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    contacts = relationship(
        "Contact",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
