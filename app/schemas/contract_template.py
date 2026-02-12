from pydantic import BaseModel, Field
from typing import Optional

class ContractTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., min_length=1)

class ContractTemplateOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    content: str
    status: str

    class Config:
        from_attributes = True

class ContractTemplateListItem(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    
    class Config:
        from_attributes = True