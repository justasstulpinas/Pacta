import secrets
from datetime import datetime, timedelta, UTC
from app.models.password_reset_token import PasswordResetToken
from app.services.email_services import send_email_verification, send_password_reset


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
        token = secrets.token_urlsafe(32)
        user.verification_token = token
        self.db.commit()
        try:
            send_email_verification(user.email, token)
        except Exception:
            pass

        self.db.refresh(user)
        return user

    def login_user(self, email: str, password: str) -> str:
        user = self.user_repo.get_by_email(email)

        if not user:
            raise InvalidCredentialsError("wrong email or password")

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("wrong email or password")

        if not user.is_verified and user.created_at:
            age = datetime.utcnow() - user.created_at.replace(tzinfo=None)
            if age.days >= 7:
                user.is_suspended = True
                self.db.commit()
                raise InvalidCredentialsError("Account suspended — email not verified within 7 days")
            if age.days == 6 and user.verification_token:
                try:
                    from app.services.email_services import send_verification_reminder
                    send_verification_reminder(user.email, user.verification_token)
                except Exception:
                    pass

        user.last_login = datetime.utcnow()
        self.db.commit()

        return create_access_token(subject=str(user.id))

    def logout_user(self, token: str) -> None:
        payload = decode_access_token(token)
        jti = payload.get("jti")
        if not jti:
            return

        self.revoked_repo.revoke(jti)

    def verify_email(self, token: str)-> None:
        user = self.db.query(User).filter(User.verification_token == token).first()
        if not user:
            raise ValidationError("Invalid or expired verification link")
        user.is_verified = True
        user.verification_token = None
        self.db.commit()
        
    def forgot_password(self, email: str) -> None:
        user = self.user_repo.get_by_email(email)
        if not user:
            return
        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            user_id= user.id,
            token= token,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            used=False,
        )
        self.db.add(reset_token)
        self.db.commit()
        try:
            send_password_reset(user.email, token)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("Failed to send password reset email to %s: %s", user.email, e)

    def reset_password(self, token: str, new_password: str) -> None:
        reset_token = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.used == False,
        ).first()
        if not reset_token:
            raise ValidationError("Invalid or expired reset link")
        if reset_token.expires_at < datetime.utcnow():
            raise ValidationError("Reset link has expired")
        user = self.user_repo.get_by_id(reset_token.user_id)
        user.hashed_password = hash_password(new_password)
        reset_token.used = True
        self.db.commit()