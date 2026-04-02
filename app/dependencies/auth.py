from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.security import oauth2_scheme, decode_access_token
from app.database import get_db
from app.core.exceptions import UnauthorizedError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.revoked_token_repository import RevokedTokenRepository

# auththikacija , kuri tikrina ar tokenas dar galioja ir grazina useri jei taip , jei ne useris 401 
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)

    jti = payload.get("jti")
    if jti:
        revoked_repo = RevokedTokenRepository(db)
        if revoked_repo.is_revoked(jti):
            raise UnauthorizedError("Token revoked")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(user_id))

    if not user:
        raise UnauthorizedError("User not found")

    return user