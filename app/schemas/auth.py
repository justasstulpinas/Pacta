from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=12, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., max_length=128)

class VerifyEmailRequest(BaseModel):
    token: str = Field(..., max_length=512)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., max_length=512)
    new_password: str = Field(..., min_length=12, max_length=128)
