from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.contract_template import ContractTemplateCreate, ContractTemplateOut
from app.services.contract_templates import create_template

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post(
    "",
    response_model=ContractTemplateOut,
    status_code=status.HTTP_201_CREATED,
)
def create_contract_template(
    payload: ContractTemplateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    template = create_template(
        db=db,
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
        content=payload.content,
    )
    return template
