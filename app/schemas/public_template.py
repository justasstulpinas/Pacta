from pydantic import BaseModel
from typing import List

class PublicTemplateOut(BaseModel):
    name: str
    description: str | None
    content: str
    fields: List[str]
    
    class Config:
        from_attributes = True

