from sqlalchemy import Integer, String,Column, UniqueConstraint
from app.database import Base

class permission(Base):

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    code= Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("code", name = "uq_permission_code")
    )