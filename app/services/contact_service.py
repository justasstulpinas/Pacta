from datetime import UTC, datetime

from pydantic import EmailStr, TypeAdapter, ValidationError as PydanticValidationError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.contact import Contact
from app.models.user import User
from app.repositories.contact_repository import ContactRepository
from app.schemas.contact import ContactCreate, ContactUpdate


EMAIL_ADAPTER = TypeAdapter(EmailStr)
# kontatu business klase kuri atsakinga uz visus su kontaktais susijusiais veiksmais nuo taisyklingo rekvizitu istraukimo iki kontaktu atnaujinimo ar kurimo
class ContactService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ContactRepository(db)

    @staticmethod
    def _normalize_text(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    def _normalize_email(self, value: str | None) -> str | None:
        normalized = self._normalize_text(value)
        if normalized is None:
            return None
        try:
            EMAIL_ADAPTER.validate_python(normalized)
        except PydanticValidationError as exc:
            raise ValidationError({"email": "Invalid email format"}) from exc
        return normalized

    def _normalize_create_payload(self, payload: ContactCreate) -> dict[str, str | None]:
        normalized = {
            "name": self._normalize_text(payload.name),
            "phone": self._normalize_text(payload.phone),
            "address": self._normalize_text(payload.address),
            "email": self._normalize_email(payload.email),
        }
        if all(value is None for value in normalized.values()):
            raise ValidationError("At least one contact field is required")
        return normalized

    def _normalize_update_payload(self, payload: ContactUpdate) -> dict[str, str | None]:
        raw_payload = payload.model_dump(exclude_unset=True)
        if not raw_payload:
            raise ValidationError("At least one field must be provided")

        normalized: dict[str, str | None] = {}
        if "name" in raw_payload:
            normalized["name"] = self._normalize_text(raw_payload["name"])
        if "phone" in raw_payload:
            normalized["phone"] = self._normalize_text(raw_payload["phone"])
        if "address" in raw_payload:
            normalized["address"] = self._normalize_text(raw_payload["address"])
        if "email" in raw_payload:
            normalized["email"] = self._normalize_email(raw_payload["email"])

        if all(value is None for value in normalized.values()):
            raise ValidationError("At least one field must be provided")
        return normalized

    def list_contacts(self, user: User, limit: int= 50, offset: int=0) -> list[Contact]:
        return self.repo.list_by_owner(user.id, limit=limit, offset=offset)

    def create_contact(self, payload: ContactCreate, user: User) -> Contact:
        normalized = self._normalize_create_payload(payload)
        return self.repo.create(
            owner_id=user.id,
            name=normalized["name"],
            phone=normalized["phone"],
            address=normalized["address"],
            email=normalized["email"],
        )
    def delete_contact(
        self, 
        contact_id: int, 
        user: User
    ) -> Contact:
        contact = self.repo.get_by_id_and_owner(contact_id, user.id)
        if not contact:
            raise NotFoundError("Contact not found")
       
        self.db.delete(contact)
        self.db.commit()
        
    
    def update_contact(
        self,
        contact_id: int,
        payload: ContactUpdate,
        user: User,
    ) -> Contact:
        contact = self.repo.get_by_id_and_owner(contact_id, user.id)
        if not contact:
            raise NotFoundError("Contact not found")

        normalized = self._normalize_update_payload(payload)
        for field_name, value in normalized.items():
            setattr(contact, field_name, value)

        contact.updated_at = datetime.now(UTC)
        return self.repo.save(contact)
