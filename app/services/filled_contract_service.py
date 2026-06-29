from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.enums import SubmissionStatus
from app.models.filled_contract import FilledContract
from app.repositories.template_repository import TemplateRepository
from app.services.policy import PolicyService
from app.services.email_services import send_contract_signed_pdf


# klase tikrina egzistavima, prieigosteses, busena ir issaugo statuso pakeitima
class FilledContractService:
    def __init__(self, db: Session, repo: TemplateRepository | None = None):
        self.db = db
        self.repo = repo or TemplateRepository(db)

    def list_all_for_user(self, current_user) -> list:
        submissions = self.repo.list_all_submissions_for_user(current_user.id)
        return [
            {
                "id": s.id,
                "template_id": s.template_id,
                "template_name": s.template.name if s.template else f"#{s.template_id}",
                "submitted_data": s.submitted_data,
                "status": s.status,
                "submitted_at": s.submitted_at,
                "confirmed_at": s.confirmed_at,
                "submitter_email": s.submitter_email,
            }
            for s in submissions
        ]

    def get_submission_by_id(
        self,
        submission_id: int,
        current_user,
    ) -> FilledContract:
        submission = self.repo.get_submission_by_id(submission_id)
        if not submission:
            raise NotFoundError("Submission not found")

        PolicyService.check_submission_access(current_user, submission)
        return submission

    def confirm_submission(
        self,
        submission_id: int,
        current_user,
    ) -> FilledContract:
        submission = self.repo.get_submission_by_id(submission_id)
        if not submission:
            raise NotFoundError("Submission not found")

        PolicyService.check_submission_access(current_user, submission)
        if submission.status != SubmissionStatus.SUBMITTED.value:
            raise BadRequestError("Submission cannot be confirmed")

        submission.status = SubmissionStatus.CONFIRMED.value
        submission.confirmed_at = func.now()
        saved = self.repo.save_submission(submission)
        try:
            if submission.submitter_email:
                from app.services.contract_submission_service import ContractSubmissionService
                service = ContractSubmissionService(self.db, self.repo)
                pdf = service.get_submission_document_pdf(submission.id, current_user)
                send_contract_signed_pdf(
                    submitter_email=submission.submitter_email,
                    template_name=submission.template.name,
                    pdf_bytes=pdf,
                    )
        except Exception:
            pass
        return saved
