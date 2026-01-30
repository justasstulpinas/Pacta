from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.database import Base

class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer,ForeignKey('roles.id'), primary_key=True)

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_role_permission")
    )