from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactOut, ContactUpdate
from app.services.contact_service import ContactService


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("", response_model=list[ContactOut])
def list_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int= 50,
    offset: int=0
):
    service = ContactService(db)
    return service.list_contacts(current_user, limit=limit, offset=offset)


@router.post("", response_model=ContactOut)
def create_contact(
    payload: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ContactService(db)
    return service.create_contact(payload, current_user)


@router.patch("/{contact_id}", response_model=ContactOut)
def update_contact(
    contact_id: int,
    payload: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ContactService(db)
    return service.update_contact(contact_id, payload, current_user)

@router.delete("/{contact_id}", status_code=204)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ContactService(db)
    service.delete_contact(contact_id, current_user)
