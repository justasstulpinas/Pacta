from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.database import Base

class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(Integer,ForeignKey('permissions.id'), primary_key=True)

    __table_args__ = (
        UniqueConstraint("role_id", "permissions_id", name="uq_role_permission")
    )