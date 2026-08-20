from pydantic import BaseModel, Field
from typing import Optional
from pydantic import ConfigDict


# pagalbinis sutarciu ivesciu standartizavimo failas
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
    
    model_config = ConfigDict(from_attributes=True)

class ContractTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    logo_x: Optional[float] = None
    logo_y: Optional[float] = None
    logo_w: Optional[float] = None
    client_sig_x: Optional[float] = None
    client_sig_y: Optional[float] = None
    user_sig_x: Optional[float] = None
    user_sig_y: Optional[float] = None