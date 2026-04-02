from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
# contactu modelis , kuris saugo userio surinktus kontaktus one to many santykiu

class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (
        Index(
            "ix_contacts_owner_updated_created",
            "owner_id",
            "updated_at",
            "created_at",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(255), nullable=True)
    phone = Column(String(64), nullable=True)
    address = Column(String(500), nullable=True)
    email = Column(String(255), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.now(UTC))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
    )

    owner = relationship("User", back_populates="contacts")
