from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError
from app.models.user import User
from app.repositories.template_repository import TemplateRepository
from app.repositories.user_profile_repository import UserProfileRepository
from app.services.filled_contract_service import FilledContractService
from app.renderers.document_renderer import render_contract_html
from app.renderers.pdf_renderer import render_pdf_from_html
from app.renderers.docx_renderer import render_docx_from_html


class ContractSubmissionService:
    """
    Legacy service for FilledContract documents.
    submitted_data and rendered_content were removed from FilledContract as part of the
    eIDAS GDPR rewrite — this service can no longer produce documents for old submissions.
    New submissions use SubmissionService (app/services/submission_service.py).
    """

    def __init__(self, db: Session, repo: TemplateRepository | None = None):
        self.db = db
        self.repo = repo or TemplateRepository(db)
        self.submission_service = FilledContractService(db, self.repo)

    def get_submission_document_html(
        self,
        submission_id: int,
        current_user: User,
    ) -> str:
        raise BadRequestError(
            "Document re-rendering is not available for legacy submissions. "
            "Signed contracts are now delivered as one-time secure downloads."
        )

    def get_submission_document_pdf(
        self,
        submission_id: int,
        current_user: User,
    ) -> bytes:
        raise BadRequestError(
            "PDF download is not available for legacy submissions. "
            "Signed contracts are now delivered as one-time secure downloads."
        )

    def get_submission_document_docx(
        self,
        submission_id: int,
        current_user: User,
    ) -> bytes:
        raise BadRequestError(
            "DOCX download is not available for legacy submissions. "
            "Signed contracts are now delivered as one-time secure downloads."
        )
