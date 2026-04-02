from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base

# pagalbinis failas user_roles tvarkymui
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)
