from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProfilePrefillOut(BaseModel):
    name_surname: str | None
    company_name: str | None
    company_code: str | None
    address: str | None
    phone_number: str | None


class ProfileOut(BaseModel):
    user_id: int
    email: str
    profile_name: str | None
    company_name: str | None
    company_code: str | None
    address: str | None
    phone_number: str | None
    avatar_url: str | None
    signature_image: str | None
    logo_image: str | None
    logo_x: float
    logo_y: float
    created_at: datetime
    updated_at: datetime
    prefill: ProfilePrefillOut

    model_config = ConfigDict(from_attributes=True)


class ProfileSignatureIn(BaseModel):
    signature_image: str


class ProfileLogoIn(BaseModel):
    logo_image: str


class ProfileLogoPositionIn(BaseModel):
    logo_x: float
    logo_y: float


class ProfileUpdate(BaseModel):
    profile_name: str | None = None
    company_name: str | None = None
    company_code: str | None = None
    address: str | None = None
    phone_number: str | None = None


class ProfileAvatarOut(BaseModel):
    avatar_url: str | None
