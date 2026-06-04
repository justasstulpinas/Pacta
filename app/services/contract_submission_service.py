from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.template_repository import TemplateRepository
from app.services.filled_contract_service import FilledContractService
from app.renderers.document_renderer import render_contract_html
from app.renderers.pdf_renderer import render_pdf_from_html
from app.renderers.docx_renderer import render_docx_from_html

# klase skirta sugeneruoti dokumenta
class ContractSubmissionService:
    def __init__(self, db: Session, repo: TemplateRepository | None = None):
        self.db = db
        self.repo = repo or TemplateRepository(db)
        self.submission_service = FilledContractService(db, self.repo)

    def get_submission_document_html(
        self,
        submission_id: int,
        current_user: User,
    ) -> str:
        submission = self.submission_service.get_submission_by_id(
            submission_id,
            current_user,
        )

        signer_name = (
            submission.submitted_data.get("client_name")
            or submission.submitted_data.get("client_vardas")
            or submission.submitter_email
        )
        return render_contract_html(
            content=submission.rendered_content,
            signature_image=submission.signature_image,
            signer_name=signer_name,
        )

    def get_submission_document_pdf(
        self,
        submission_id: int,
        current_user: User,
    ) -> bytes:
        html = self.get_submission_document_html(submission_id, current_user)
        return render_pdf_from_html(html)

    def get_submission_document_docx(
        self,
        submission_id: int,
        current_user: User,
    ) -> bytes:
        html = self.get_submission_document_html(submission_id, current_user)
        return render_docx_from_html(html)
