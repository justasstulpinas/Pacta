from pydantic import BaseModel
from datetime import datetime
from typing import Any, Dict, Optional


class FilledContractResponse(BaseModel):
    id: int
    template_id: int
    link_id: int
    submitted_data: Dict[str, Any]
    rendered_content: str
    submitted_at: datetime
    ip_address: str
    user_agent: Optional[str]
    submission_hash: str

    class Config:
        from_attributes = True