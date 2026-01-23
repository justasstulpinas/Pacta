# app/services/auth_service.py

from sqlalchemy.orm import Session

from app.crud.user import get_user_by_email, get_user_by_id
from app.core.security import verify_password, create_access_token, decode_access_token
from app.models.user import User
from app.core.exceptions import InvalidCredentialsError
from app.core.security import decode_access_token



def login_user(
        db: Session,
        email: str,
        password: str
) -> str:
    
    user = get_user_by_email(db, email)

    if not user:
        raise InvalidCredentialsError()
    
    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()
    
    access_token = create_access_token(
        subject=str(user.id)
    )

    return access_token

def get_current_user_from_token(db: Session, token: str) -> User:
    payload = decode_access_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidCredentialsError()

    user = get_user_by_id(db, int(user_id))
    if not user:
        raise InvalidCredentialsError()

    return user