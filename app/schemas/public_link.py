from typing import Dict
from pydantic import BaseModel, Field
from datetime import datetime
from pydantic import ConfigDict

class PublicLinkCreate(BaseModel):
    template_id: int
    expires_in_hours: int
    prefill: Dict[str, str] = Field(default_factory=dict)

class PublicLinkOut(BaseModel):
    id: int
    token: str
    expires_at: datetime
    is_revoked: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
