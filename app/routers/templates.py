from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.contract_template import (
    ContractTemplateCreate,
    ContractTemplateOut,
    ContractTemplateUpdate
)
from app.schemas.filled_contract import FilledContractResponse

from app.services.contract_service import ContractService
from app.services.template_service import TemplateService


router = APIRouter(
    prefix="/templates",
    tags=["templates"],
)


@router.post(
    "",
    response_model=ContractTemplateOut,
    status_code=status.HTTP_201_CREATED,
)
def create_template(
    payload: ContractTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.create_template(payload, current_user)


@router.get(
    "",
    response_model=list[ContractTemplateOut],
)
def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.list_user_templates(current_user)


@router.get(
    "/{template_id}",
    response_model=ContractTemplateOut,
)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.get_template_by_id(template_id, current_user)


@router.get(
    "/{template_id}/submissions",
    response_model=list[FilledContractResponse],
)
def get_submissions(
    template_id: int,
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ContractService(db)
    return service.get_template_submissions(
        template_id=template_id,
        user=current_user,
        limit=limit,
        offset=offset,
        status=status,
    )


@router.post(
    "/{template_id}/duplicate",
    response_model=ContractTemplateOut,
    status_code=status.HTTP_201_CREATED,
)
def duplicate_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.duplicate_template(template_id, current_user)


@router.patch(
    "/{template_id}/activate",
    response_model=ContractTemplateOut,
)
def activate_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.activate_template(template_id, current_user)


@router.patch(
    "/{template_id}/archive",
    response_model=ContractTemplateOut,
)
def archive_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.archive_template(template_id, current_user)


@router.delete(
    "/{template_id}",
    response_model=ContractTemplateOut,
)
def soft_delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.soft_delete_template(template_id, current_user)

@router.put(
    "/{template_id}",
    response_model=ContractTemplateOut,
)
def update_template(
    template_id: int,
    payload: ContractTemplateUpdate,
    db: Session =Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.update_template(template_id, payload, current_user)
