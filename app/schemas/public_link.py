from typing import Dict, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from pydantic import ConfigDict

class PublicLinkCreate(BaseModel):
    template_id: int
    expires_in_hours: int = Field(..., ge=1, le=8760)
    prefill: Dict[str, str] = Field(default_factory=dict)
    recipient_email: Optional[EmailStr] = Field(None, max_length=254)

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
