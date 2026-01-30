from sqlalchemy.orm import Session

from app.crud.user import get_user_by_email, get_user_by_id
from app.core.security import verify_password, create_access_token, decode_access_token
from app.models.user import User
from app.core.exceptions import InvalidCredentialsError, ForbiddenError
from app.core.security import decode_access_token
from app.crud.revoked_token import revoke_token
from app.models.user import User


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

def get_current_user_from_payload(
        db: Session,
        payload: dict,
) -> User:
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidCredentialsError()
    
    user = get_user_by_id(db, int(user_id))
    if not user:
        raise InvalidCredentialsError()
    
    return user

def get_current_user_from_token(
        db: Session, 
        payload: dict
) -> User:

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidCredentialsError()

    user = get_user_by_id(db, int(user_id))
    if not user:
        raise InvalidCredentialsError()

    return user

def logout_user(db: Session, token_payload: dict):
    jti = token_payload.get("jti")
    if not jti:
        return
    
    revoke_token(db, jti)
    # serveris paima tik jti ir pazymi ji kaip revoked
