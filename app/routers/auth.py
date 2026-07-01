from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import oauth2_scheme
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, UserCreate, VerifyEmailRequest, ForgotPasswordRequest, ResetPasswordRequest


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register")
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    user = service.register_user(email=data.email, password=data.password)
    return {
        "id": user.id,
        "email": user.email,
    }


@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    access_token = service.login_user(
        email=data.email,
        password=data.password,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/token")
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    access_token = service.login_user(
        email=form_data.username,
        password=form_data.password,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "roles": [r.name for r in current_user.roles],
    }


@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    service.logout_user(token)
    return {"status": "logged_out"}

@router.post("/verify-email")
def verify_email(
    data: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    service.verify_email(data.token)
    return {"status": "email_verified"}


@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    service.forgot_password(data.email)
    return {"status": "ok"}


@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    service.reset_password(data.token, data.new_password)
    return {"status": "password_reset"}
