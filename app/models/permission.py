from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
    )

    __table_args__ = (
        UniqueConstraint("code", name="uq_permission_code"),
    )
permission = Permission
