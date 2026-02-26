from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.public_link import PublicLinkCreate, PublicLinkOut
from app.services.link_service import LinkService
from app.schemas.public_template import PublicTemplateOut

router = APIRouter(prefix='/links', tags=["links"])

@router.post("", response_model=PublicLinkOut)
def create_link(
    payload: PublicLinkCreate,
    db: Session= Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LinkService(db)
    return service.create_public_link(
        template_id = payload.template_id,
        expires_in_hours= payload.expires_in_hours,
        user = current_user,
    )

@router.get("/public/{token}", response_model=PublicTemplateOut)
def get_public_template(
    token: str,
    db: Session = Depends(get_db),
):
    service = LinkService(db)
    return service.get_public_template(token)