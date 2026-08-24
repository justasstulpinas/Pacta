from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class ContactCreate(BaseModel):
    name: str | None = Field(None, max_length=200)
    phone: str | None = Field(None, max_length=50)
    address: str | None = Field(None, max_length=500)
    email: str | None = Field(None, max_length=254)


class ContactUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    phone: str | None = Field(None, max_length=50)
    address: str | None = Field(None, max_length=500)
    email: str | None = Field(None, max_length=254)


class ContactOut(BaseModel):
    id: int
    owner_id: int
    name: str | None
    phone: str | None
    address: str | None
    email: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
