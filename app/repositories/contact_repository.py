from sqlalchemy.orm import Session

from app.models.contact import Contact

# klase skirta parodyti visoms userio sutartims , rodyti pagal owneri kuris prisijunges, arba pagal id ir owneri
class ContactRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_owner(self, owner_id: int) -> list[Contact]:
        return (
            self.db.query(Contact)
            .filter(Contact.owner_id == owner_id)
            .order_by(
                Contact.updated_at.desc(),
                Contact.created_at.desc(),
            )
            .all()
        )
    def get_by_id_and_owner(self, contact_id: int, owner_id: int) -> Contact | None:
        return (
            self.db.query(Contact)
            .filter(
                Contact.id == contact_id,
                Contact.owner_id == owner_id,
            )
            .first()
        )

    def create(
        self,
        *,
        owner_id: int,
        name: str | None,
        phone: str | None,
        address: str | None,
        email: str | None,
    ) -> Contact:
        contact = Contact(
            owner_id=owner_id,
            name=name,
            phone=phone,
            address=address,
            email=email,
        )
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def save(self, contact: Contact) -> Contact:
        self.db.commit()
        self.db.refresh(contact)
        return contact
