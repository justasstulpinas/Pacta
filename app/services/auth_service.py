from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCredentialsError, ValidationError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.role import Role
from app.repositories.revoked_token_repository import RevokedTokenRepository
from app.repositories.user_repository import UserRepository
from app.models.user import User

# authentikavimo klase kuris yra atsakinga uz userio register, login. logout
class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.revoked_repo = RevokedTokenRepository(db)

    def register_user(self, email: str, password: str) -> User:
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValidationError("User already exists")

        hashed_password = hash_password(password)
        user = User(email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.flush()

        creator_role = self.db.query(Role).filter(Role.name == "creator").first()
        if creator_role:
            user.roles.append(creator_role)

        self.db.commit()
        self.db.refresh(user)
        return user

    def login_user(self, email: str, password: str) -> str:
        user = self.user_repo.get_by_email(email)

        if not user:
            raise InvalidCredentialsError("wrong email or password")

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("wrong email or password")

        return create_access_token(subject=str(user.id))

    def logout_user(self, token: str) -> None:
        payload = decode_access_token(token)
        jti = payload.get("jti")
        if not jti:
            return

        self.revoked_repo.revoke(jti)
