from sqlalchemy.orm import Session

from app.models.revoked_token import RevokedToken


class RevokedTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def is_revoked(self, jti: str) -> bool:
        return (
            self.db.query(RevokedToken)
            .filter(RevokedToken.jti == jti)
            .first()
            is not None
        )

    def revoke(self, jti: str) -> None:
        self.db.add(RevokedToken(jti=jti))
        self.db.commit()
