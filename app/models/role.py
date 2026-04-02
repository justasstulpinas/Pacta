from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base

# roliu duombaze, kurioje yra surasytos roles
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
    )

    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
    )
