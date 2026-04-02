from datetime import datetime

from pydantic import BaseModel, ConfigDict

# pagalbinis kontaktu ivesti standartizuojantis fialas
class ContactCreate(BaseModel):
    name: str | None = None
    phone: str | None = None
    address: str | None = None
    email: str | None = None


class ContactUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    address: str | None = None
    email: str | None = None


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
