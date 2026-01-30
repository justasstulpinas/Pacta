from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.security import oauth2_scheme, decode_access_token
from app.database import get_db
from app.services.auth_service import get_current_user_from_payload
from app.crud.revoked_token import is_token_revoked
from app.core.exceptions import InvalidCredentialsError


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_access_token(token)

    jti = payload.get("jti")
    if jti and is_token_revoked(db, jti):
        raise InvalidCredentialsError()

    return get_current_user_from_payload(db, payload)
