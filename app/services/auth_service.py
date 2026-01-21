from sqlalchemy.orm import Session

from app.crud.user import get_user_by_email
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.core.exceptions import InvalidCredentialsError


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

