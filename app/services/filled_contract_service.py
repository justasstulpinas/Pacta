from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.filled_contract import FilledContract
from app.models.contract_template import ContractTemplate
from app.core.exceptions import NotFoundError, ForbiddenError, BadRequestError


def get_submission_by_id(
    db: Session,
    submission_id: int,
    current_user
) -> FilledContract:

    submission = (
        db.query(FilledContract)
        .filter(FilledContract.id == submission_id)
        .first()
    )

    if not submission:
        raise NotFoundError("Submission not found")

    template = (
        db.query(ContractTemplate)
        .filter(ContractTemplate.id == submission.template_id)
        .first()
    )

    if not template or template.is_deleted:
        raise NotFoundError("Template not found")

    if template.owner_id != current_user.id and not current_user.is_admin:
        raise ForbiddenError("Access denied")

    return submission

def confirm_contract(
        db: Session,
        submision_id: int,
        current_user
) -> FilledContract:
    
    submission = (
        db.query(FilledContract)
        .filter(FilledContract.id == submision_id)
        .first()
    )
    if not submission:
        raise NotFoundError('Submission not found')
    
    template = (
        db.query(ContractTemplate)
        .filter(ContractTemplate == submission.template_id)
        .first()
    )
    
    if not template or template.is_deleted:
        raise NotFoundError("template not found")
    if template.owner_id != current_user.id and not current_user.is_admin:
        raise ForbiddenError("access denied")
    if submission.status != "submitted":
        raise BadRequestError("contract cannot be confirmed")
    
    submission.status = "confirmed"
    submission.confirmed_at = func.now()

    db.commit()
    db.refresh(submission)

    return submission