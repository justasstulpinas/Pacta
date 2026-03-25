from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.filled_contract import FilledContract
from app.models.contract_template import ContractTemplate

from app.core.exceptions import NotFoundError, ForbiddenError, BadRequestError

from app.services.policy import require_owner_or_admin

from app.repositories.template_repository import TemplateRepository

def _get_submission(db: Session, submission_id: int) -> FilledContract:
    repo = TemplateRepository(db)
    submission = repo.get_submission_by_id(submission_id)

    if not submission:
        raise NotFoundError("Submission not found")

    return submission


def _get_template(db: Session, template_id: int) -> ContractTemplate:
    repo = TemplateRepository(db)
    template = repo.get_active_by_id(template_id)

    if not template:
        raise NotFoundError("Template not found")

    return template

def get_submission_by_id(
    db: Session,
    submission_id: int,
    current_user,
) -> FilledContract:

    submission = _get_submission(db, submission_id)
    template = _get_template(db, submission.template_id)

    require_owner_or_admin(template.owner_id, current_user)

    return submission


def confirm_submission(
    db: Session,
    submission_id: int,
    current_user,
) -> FilledContract:

    submission = _get_submission(db, submission_id)
    template = _get_template(db, submission.template_id)

    require_owner_or_admin(template.owner_id, current_user)

    if submission.status != "submitted":
        raise BadRequestError("Submission cannot be confirmed")

    submission.status = "confirmed"
    submission.confirmed_at = func.now()

    db.commit()
    db.refresh(submission)

    return submission

def confirm_contract(
        db,
        submission_id: int,
        current_user,
):
    return confirm_submission(db, submission_id, current_user)