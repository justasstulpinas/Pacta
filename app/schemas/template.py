from pydantic import BaseModel
from datetime import datetime

class TemplateRead(BaseModel):
    id: int
    name: str
    description: str | None
    content: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }