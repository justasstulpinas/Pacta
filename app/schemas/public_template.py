from pydantic import BaseModel, ConfigDict
from typing import List


class PublicTemplateOut(BaseModel):
    name: str
    description: str | None
    content: str
    fields: List[str]
    
    model_config = ConfigDict(from_attributes=True)

