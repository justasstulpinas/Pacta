from sqlalchemy.orm import Session
from app.models.revoked_token import RevokedToken


def is_token_revoked(db: Session, jti: str):
    return db.query(RevokedToken).filter(RevokedToken.jti == jti).first() is not None


def revoke_token(db: Session, jti:str):
    db.add(RevokedToken(jti=jti))
    db.commit()
    # patikrinama ar tokenas revoked, jei taip tada ivyksta revoke_token