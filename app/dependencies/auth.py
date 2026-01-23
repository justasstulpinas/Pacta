from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.security import oauth2_scheme
from app.database import get_db
from app.services.auth_service import get_current_user_from_token


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    return get_current_user_from_token(db, token)
