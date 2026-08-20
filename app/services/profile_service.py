from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import User
from app.models.user_profile import UserProfile
from app.repositories.user_profile_repository import UserProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.profile import ProfileAvatarOut, ProfileLogoIn, ProfileLogoPositionIn, ProfileOut, ProfilePrefillOut, ProfileSignatureIn, ProfileUpdate

# profilio tvarkymo klase
class ProfileService:
    ALLOWED_AVATAR_MIME_TYPES = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    MAX_AVATAR_SIZE = 5 * 1024 * 1024
    AVATAR_UPLOAD_DIR = Path("app/uploads/avatars")
    AVATAR_PUBLIC_PREFIX = "/uploads/avatars"
    MAGIC_BYTES = {
    "image/jpeg": (b'\xff\xd8\xff', 3),
    "image/png": (b'\x89PNG', 4),
    "image/webp": (b'WEBP', 4),
}


    def __init__(self, db):
        self.db = db
        self.profile_repo = UserProfileRepository(db)
        self.user_repo = UserRepository(db)

    @staticmethod
    def _normalize_text(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    def _ensure_profile(self, user_id: int) -> UserProfile:
        profile = self.profile_repo.get_by_user_id(user_id)
        if profile:
            return profile
        return self.profile_repo.create_for_user(user_id)

    @staticmethod
    def _to_profile_out(user: User, profile: UserProfile) -> ProfileOut:
        return ProfileOut(
            user_id=user.id,
            email=user.email,
            profile_name=profile.profile_name,
            company_name=profile.company_name,
            company_code=profile.company_code,
            address=profile.address,
            phone_number=profile.phone_number,
            avatar_url=profile.avatar_url,
            signature_image=profile.signature_image,
            logo_image=profile.logo_image,
            logo_x=profile.logo_x if profile.logo_x is not None else 5.0,
            logo_y=profile.logo_y if profile.logo_y is not None else 5.0,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            prefill=ProfilePrefillOut(
                name_surname=profile.profile_name,
                company_name=profile.company_name,
                company_code=profile.company_code,
                address=profile.address,
                phone_number=profile.phone_number,
            ),
        )

    def get_profile(self, current_user: User) -> ProfileOut:
        user = self.user_repo.get_by_id(current_user.id)
        if not user:
            raise NotFoundError("User not found")
        profile = self._ensure_profile(user.id)
        return self._to_profile_out(user, profile)

    def update_profile(
        self,
        payload: ProfileUpdate,
        current_user: User,
    ) -> ProfileOut:
        user = self.user_repo.get_by_id(current_user.id)
        if not user:
            raise NotFoundError("User not found")

        profile = self._ensure_profile(user.id)
        updates = payload.model_dump(exclude_unset=True)

        if "profile_name" in updates:
            profile.profile_name = self._normalize_text(payload.profile_name)
        if "company_name" in updates:
            profile.company_name = self._normalize_text(payload.company_name)
        if "company_code" in updates:
            profile.company_code = self._normalize_text(payload.company_code)
        if "address" in updates:
            profile.address = self._normalize_text(payload.address)
        if "phone_number" in updates:
            profile.phone_number = self._normalize_text(payload.phone_number)

        profile.updated_at = datetime.now(UTC)
        saved = self.profile_repo.save(profile)
        return self._to_profile_out(user, saved)

    def delete_profile_account(self, current_user: User) -> None:
        user = self.user_repo.get_by_id(current_user.id)
        if not user:
            raise NotFoundError("User not found")

        profile = self.profile_repo.get_by_user_id(user.id)
        if profile and profile.avatar_url:
            self._remove_avatar_file(profile.avatar_url)

        self.user_repo.delete(user)

    def upload_avatar(
        self,
        *,
        file_bytes: bytes,
        content_type: str | None,
        current_user: User,
    ) -> ProfileAvatarOut:
        user = self.user_repo.get_by_id(current_user.id)
        if not user:
            raise NotFoundError("User not found")
        if content_type not in self.ALLOWED_AVATAR_MIME_TYPES:
            raise ValidationError("Invalid image type")
        expected_signature, length = self.MAGIC_BYTES[content_type]
        if file_bytes[:length] != expected_signature:
            raise ValidationError("Invalid image type")
        if len(file_bytes) > self.MAX_AVATAR_SIZE:
            raise ValidationError("Image is too large")

        profile = self._ensure_profile(user.id)

        self.AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        extension = self.ALLOWED_AVATAR_MIME_TYPES[content_type]
        filename = f"{uuid4().hex}{extension}"
        avatar_path = self.AVATAR_UPLOAD_DIR / filename
        avatar_path.write_bytes(file_bytes)

        old_avatar_url = profile.avatar_url
        profile.avatar_url = f"{self.AVATAR_PUBLIC_PREFIX}/{filename}"
        profile.updated_at = datetime.now(UTC)
        saved = self.profile_repo.save(profile)

        if old_avatar_url:
            self._remove_avatar_file(old_avatar_url)

        return ProfileAvatarOut(avatar_url=saved.avatar_url)

    def delete_avatar(self, current_user: User) -> ProfileAvatarOut:
        user = self.user_repo.get_by_id(current_user.id)
        if not user:
            raise NotFoundError("User not found")

        profile = self._ensure_profile(user.id)
        old_avatar_url = profile.avatar_url
        profile.avatar_url = None
        profile.updated_at = datetime.now(UTC)
        self.profile_repo.save(profile)

        if old_avatar_url:
            self._remove_avatar_file(old_avatar_url)

        return ProfileAvatarOut(avatar_url=None)

    def save_signature(self, payload: ProfileSignatureIn, current_user: User) -> ProfileOut:
        user = self.user_repo.get_by_id(current_user.id)
        if not user:
            raise NotFoundError("User not found")
        profile = self._ensure_profile(user.id)
        profile.signature_image = payload.signature_image
        profile.updated_at = datetime.now(UTC)
        saved = self.profile_repo.save(profile)
        return self._to_profile_out(user, saved)

    def delete_signature(self, current_user: User) -> ProfileOut:
        user = self.user_repo.get_by_id(current_user.id)
        if not user:
            raise NotFoundError("User not found")
        profile = self._ensure_profile(user.id)
        profile.signature_image = None
        profile.updated_at = datetime.now(UTC)
        saved = self.profile_repo.save(profile)
        return self._to_profile_out(user, saved)

    def save_logo(self, payload: ProfileLogoIn, current_user: User) -> ProfileOut:
        user = self.user_repo.get_by_id(current_user.id)
        if not user:
            raise NotFoundError("User not found")
        profile = self._ensure_profile(user.id)
        profile.logo_image = payload.logo_image
        profile.updated_at = datetime.now(UTC)
        saved = self.profile_repo.save(profile)
        return self._to_profile_out(user, saved)

    def delete_logo(self, current_user: User) -> ProfileOut:
        user = self.user_repo.get_by_id(current_user.id)
        if not user:
            raise NotFoundError("User not found")
        profile = self._ensure_profile(user.id)
        profile.logo_image = None
        profile.updated_at = datetime.now(UTC)
        saved = self.profile_repo.save(profile)
        return self._to_profile_out(user, saved)

    def update_logo_position(self, payload: ProfileLogoPositionIn, current_user: User) -> ProfileOut:
        user = self.user_repo.get_by_id(current_user.id)
        if not user:
            raise NotFoundError("User not found")
        profile = self._ensure_profile(user.id)
        profile.logo_x = max(0.0, min(95.0, payload.logo_x))
        profile.logo_y = max(0.0, min(95.0, payload.logo_y))
        profile.updated_at = datetime.now(UTC)
        saved = self.profile_repo.save(profile)
        return self._to_profile_out(user, saved)

    def _remove_avatar_file(self, avatar_url: str) -> None:
        prefix = f"{self.AVATAR_PUBLIC_PREFIX}/"
        if not avatar_url.startswith(prefix):
            return

        filename = avatar_url[len(prefix):]
        safe_name = Path(filename).name
        if safe_name != filename:
            return

        path = self.AVATAR_UPLOAD_DIR / safe_name
        if path.exists():
            path.unlink()
