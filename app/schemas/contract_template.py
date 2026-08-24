from pydantic import BaseModel, Field
from typing import Optional
from pydantic import ConfigDict


class ContractTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., min_length=1, max_length=500_000)

class ContractTemplateOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    content: str
    status: str
    logo_x: float = 5.0
    logo_y: float = 5.0
    logo_w: float = 15.0
    client_sig_x: Optional[float] = None
    client_sig_y: Optional[float] = None
    user_sig_x: Optional[float] = None
    user_sig_y: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class ContractTemplateListItem(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    content: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ContractTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, max_length=500_000)
    logo_x: Optional[float] = None
    logo_y: Optional[float] = None
    logo_w: Optional[float] = None
    client_sig_x: Optional[float] = None
    client_sig_y: Optional[float] = None
    user_sig_x: Optional[float] = None
    user_sig_y: Optional[float] = None
