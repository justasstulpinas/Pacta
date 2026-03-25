from sqlalchemy.orm import Session

from app.crud.user import get_user_by_email, get_user_by_id
from app.crud.revoked_token import revoke_token

from app.core.security import verify_password, create_access_token
from app.core.exceptions import InvalidCredentialsError

from app.models.user import User


def login_user(db: Session, email: str, password: str) -> str:
    user = get_user_by_email(db, email)

    if not user:
        raise InvalidCredentialsError("wrong email or password")

    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError("wrong email or password")

    return create_access_token(subject=str(user.id))


def get_current_user(db: Session, payload: dict) -> User:
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidCredentialsError("Invalid token payload")

    user = get_user_by_id(db, int(user_id))
    if not user:
        raise InvalidCredentialsError("User not found")

    return user


def logout_user(db: Session, token_payload: dict) -> None:
    jti = token_payload.get("jti")
    if not jti:
        return

    revoke_token(db, jti)