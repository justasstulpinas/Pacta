from fastapi import APIRouter, Body, Depends, Request
from sqlalchemy.orm import Session
from typing import Dict

from app.limiter import limiter
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.public_link import PublicLinkCreate, PublicLinkOut
from app.services.link_service import LinkService
from app.schemas.public_template import PublicTemplateOut
from app.schemas.filled_contract import ContractSubmitRequest

router = APIRouter(prefix="/links", tags=["links"])

@router.post("", response_model=PublicLinkOut)
def create_link(
    payload: PublicLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LinkService(db)
    return service.create_public_link(
        template_id=payload.template_id,
        expires_in_hours=payload.expires_in_hours,
        user=current_user,
        prefill=payload.prefill,
    )

@router.get("/public/{token}", response_model=PublicTemplateOut)
def get_public_template(
    token: str,
    db: Session = Depends(get_db),
):
    service = LinkService(db)
    return service.get_public_template(token)


@router.post("/public/{token}/submit")
@limiter.limit("5/minute")
async def submit_public_contract(
    token: str,
    request: Request,
    body: ContractSubmitRequest,
    db: Session = Depends(get_db),
):
    service = LinkService(db)
    return service.submit_public_contract(
        token=token,
        payload=body.payload,
        signature_image= body.signature_image,
        ip=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent"),
    )

@router.delete("/{link_id}", response_model=PublicLinkOut)
def revoke_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LinkService(db)
    return service.revoke_public_link(link_id, current_user)