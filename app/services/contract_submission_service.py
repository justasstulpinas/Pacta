from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.filled_contract import FilledContract
from app.models.contract_template import ContractTemplate
from app.renderers.document_renderer import render_contract_html
from app.renderers.pdf_renderer import render_pdf_from_html
from app.renderers.docx_renderer import render_docx_from_html


def get_submission_document_html(
    db: Session,
    submission_id: int,
    current_user,
):


    submission = (
        db.query(FilledContract)
        .filter(FilledContract.id == submission_id)
        .first()
    )

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    template = (
        db.query(ContractTemplate)
        .filter(
            ContractTemplate.id == submission.template_id,
            ContractTemplate.is_deleted == False,
        )
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    is_owner = template.owner_id == current_user.id
    is_admin = getattr(current_user, "is_admin", False)

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    html = render_contract_html(
        contract_id=submission.id,
        template_id=submission.template_id,
        content=submission.rendered_content,
        submitted_at=submission.submitted_at,
    )

    return html

def get_submission_document_pdf(
    db: Session,
    submission_id: int,
    current_user,
):

    html = get_submission_document_html(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )

    pdf = render_pdf_from_html(html)

    return pdf

def get_submission_document_docx(
    db: Session,
    submission_id: int,
    current_user,
):

    html = get_submission_document_html(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )

    docx = render_docx_from_html(html)

    return docx