from sqlalchemy import Column, Integer, String, Boolean
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
