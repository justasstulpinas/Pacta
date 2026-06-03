from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any, Dict, Optional



# pagalbinis uzpildytu sutarciu ivesciu standartizavimo failas
class FilledContractResponse(BaseModel):
    id: int
    template_id: int
    template_version: Optional[int]
    link_id: int
    submitted_data: Dict[str, Any]
    rendered_content: str
    status: str
    submitted_at: datetime
    confirmed_at: Optional[datetime]
    ip_address: str
    user_agent: Optional[str]
    signature_image: Optional[str] = None
    submission_hash: str
    submitter_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class FilledContractListItem(BaseModel):
    id: int
    template_id: int
    template_name: str
    submitted_data: Dict[str, Any]
    status: str
    submitted_at: datetime
    confirmed_at: Optional[datetime]
    submitter_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ContractSubmitRequest(BaseModel):
    payload: Dict[str, str]
    signature_image: Optional[str] = None
    submitter_email: Optional[str] = None

