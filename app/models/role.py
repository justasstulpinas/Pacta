from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    permissions = relationship(
        "Permission",
        secondary="role_permission",
        lazy="selectin"
    )