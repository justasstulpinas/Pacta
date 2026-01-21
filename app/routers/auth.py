from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import UserCreate, LoginRequest
from app.services.auth_service import login_user
from app.core.security import hash_password
from app.crud.user import get_user_by_email, create_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/register")
def register(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    if get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    user = create_user(
        db,
        email=data.email,
        hashed_password=hash_password(data.password)
    )

    return {
        "id": user.id,
        "email": user.email
    }


@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    access_token = login_user(
        db=db,
        email=data.email,
        password=data.password
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



# day4 sukurtas router/auth.py router priima http request, validuoja input per schemas,
# perduoda duomenis service sluoksniui,paverčia rezultatą į HTTP response.

# day 5 pakeistas try/except i paprasta return