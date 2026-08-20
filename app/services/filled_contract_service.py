import logging

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.enums import SubmissionStatus
from app.models.filled_contract import FilledContract
from app.repositories.template_repository import TemplateRepository
from app.services.policy import PolicyService
from app.services.email_services import send_submission_confirmation

logger = logging.getLogger(__name__)


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

        submitter_email = submission.submitter_email
        template_name = submission.template.name

        submission.status = SubmissionStatus.CONFIRMED.value
        submission.confirmed_at = func.now()
        saved = self.repo.save_submission(submission)

        try:
            if submitter_email:
                send_submission_confirmation(
                    submitter_email=submitter_email,
                    template_name=template_name,
                )
        except Exception:
            logger.exception("Failed to send signed PDF email for submission %s", submission.id)
        return saved
    
    def cancel_submission(
            self,
            submission_id: int,
            current_user,
    ) -> FilledContract:
        submission = self.repo.get_submission_by_id(submission_id)
        if not submission:
            raise NotFoundError("Submission not found")
        
        PolicyService.check_submission_access(current_user, submission)
        if submission.status not in (SubmissionStatus.SUBMITTED.value, SubmissionStatus.CONFIRMED.value):
            raise BadRequestError("Submission can not be canceled")
         
        submission.status = SubmissionStatus.CANCELLED.value
        saved = self.repo.save_submission(submission)
        return saved
        
    def complete_submission(
            self,
            submission_id: int,
            current_user,
    ) -> FilledContract:
        submission = self.repo.get_submission_by_id(submission_id)
        if not submission:
            raise NotFoundError("Submission not found")
        
        PolicyService.check_submission_access(current_user, submission)
        if submission.status != SubmissionStatus.CONFIRMED.value:
            raise BadRequestError("Submission must be confirmed to be completed")
         
        submission.status = SubmissionStatus.COMPLETED.value
        saved = self.repo.save_submission(submission)
        return saved
        

