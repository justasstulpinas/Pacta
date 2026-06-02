from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.enums import SubmissionStatus
from app.models.filled_contract import FilledContract
from app.repositories.template_repository import TemplateRepository
from app.services.policy import PolicyService
from app.services.email_services import send_submission_confirmation

# klase tikrina egzistavima, prieigosteses, busena ir issaugo statuso pakeitima
class FilledContractService:
    def __init__(self, db: Session, repo: TemplateRepository | None = None):
        self.db = db
        self.repo = repo or TemplateRepository(db)

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
        try:
            send_submission_confirmation(
            submitter_email=submission.submitter_email,
            template_name=submission.template.name)
        except Exception:
            pass
        return self.repo.save_submission(submission)
