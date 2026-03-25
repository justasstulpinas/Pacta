from pydantic import BaseModel
from datetime import datetime
from pydantic import ConfigDict

class PublicLinkCreate(BaseModel):
    template_id: int
    expires_in_hours: int

class PublicLinkOut(BaseModel):
    id: int
    token: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)