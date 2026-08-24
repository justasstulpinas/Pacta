from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import Any, Dict, Optional


class FilledContractResponse(BaseModel):
    id: int
    template_id: int
    template_version: Optional[int] = None
    link_id: int
    status: str
    submitted_at: datetime
    confirmed_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    signature_image: Optional[str] = None
    submission_hash: Optional[str] = None
    submitter_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class FilledContractListItem(BaseModel):
    id: int
    template_id: int
    template_name: str
    status: str
    submitted_at: datetime
    confirmed_at: Optional[datetime] = None
    submitter_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ContractSubmitRequest(BaseModel):
    payload: Dict[str, str] = Field(default_factory=dict)
    signature_image: Optional[str] = Field(None, max_length=2_000_000)
    submitter_email: Optional[EmailStr] = Field(None, max_length=254)
