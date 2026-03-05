from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.filled_contract import FilledContractResponse
from app.services.filled_contract_service import get_submission_by_id, confirm_contract



router = APIRouter(
    prefix="/contracts",
    tags=["contracts"])


@router.get(
    "/submissions/{submission_id}",
    response_model=FilledContractResponse
)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    submission = get_submission_by_id(
        db=db,
        submission_id=submission_id,
        current_user=current_user
    )

    return submission

@router.post(
    "/submissions/{submission_id}/confirm",
    response_model=FilledContractResponse
)
def confirm_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    submission = confirm_contract(
        db=db,
        submision_id=submission_id,
        current_user=current_user
    )
    return submission