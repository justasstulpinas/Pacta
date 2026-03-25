from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError

from app.models.filled_contract import FilledContract
from app.models.contract_template import ContractTemplate
from app.models.user import User

from app.services.policy import require_owner_or_admin

from app.renderers.document_renderer import render_contract_html
from app.renderers.pdf_renderer import render_pdf_from_html
from app.renderers.docx_renderer import render_docx_from_html

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

def get_submission_document_html(
        db: Session,
        submission_id: int,
        current_user: User,
        ) -> str:
    submission = _get_submission(db, submission_id)
    template = _get_template(db, submission.template_id)

    require_owner_or_admin(template.owner_id, current_user)

    return render_contract_html(
        contract_id=submission.id,
        template_id=submission.template_id,
        content=submission.rendered_content,
        submitted_at=submission.submitted_at,
    )
def get_submission_document_pdf(
    db: Session,
    submission_id: int,
    current_user: User,
) -> bytes:

    html = get_submission_document_html(db, submission_id, current_user)
    return render_pdf_from_html(html)

def get_submission_document_docx(
    db: Session,
    submission_id: int,
    current_user: User,
) -> bytes:

    html = get_submission_document_html(db, submission_id, current_user)
    return render_docx_from_html(html)