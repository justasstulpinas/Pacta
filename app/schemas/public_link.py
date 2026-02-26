from pydantic import BaseModel
from datetime import datetime

class PublicLinkCreate(BaseModel):
    template_id: int
    expires_in_hours: int

class PublicLinkOut(BaseModel):
    id: int
    token: str
    expires_at: datetime

    class Config:
        from_attributes = True