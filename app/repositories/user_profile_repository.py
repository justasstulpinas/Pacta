from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile

# vartotojo profilio sukurimo ir parodymo klase
class UserProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> UserProfile | None:
        return (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

    def create_for_user(self, user_id: int) -> UserProfile:
        profile = UserProfile(user_id=user_id)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def save(self, profile: UserProfile) -> UserProfile:
        self.db.commit()
        self.db.refresh(profile)
        return profile
