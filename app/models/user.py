from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key= True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    roles= relationship(
        "Role",
        secondary="user_roles",
        lazy="selectin"
    )
    contract_templates = relationship(
    "ContractTemplate",
    back_populates="owner",
    cascade="all, delete-orphan",
)


# day 2 sukurtas user modelis