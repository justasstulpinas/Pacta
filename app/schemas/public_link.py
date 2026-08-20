from typing import Dict, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from pydantic import ConfigDict

class PublicLinkCreate(BaseModel):
    template_id: int
    expires_in_hours: int
    prefill: Dict[str, str] = Field(default_factory=dict)
    # Optional: if set, system emails the access link + code to the client directly
    recipient_email: Optional[EmailStr] = None
class PublicLinkOut(BaseModel):
    id: int
    token: str
    expires_at: datetime
    is_revoked: bool
    logo_x: float
    logo_y: float
    logo_w: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
