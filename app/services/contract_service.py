from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError

from app.models.contract_template import ContractTemplate
from app.models.filled_contract import FilledContract
from app.models.user import User

from app.services.authorization import is_admin

from app.repositories.template_repository import TemplateRepository


class ContractService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TemplateRepository(db)

    def get_template_submissions(
        self,
        template_id: int,
        user: User,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
    ) -> list[FilledContract]:

        template = self.repo.get_by_id(template_id) 

        if not template:
            raise NotFoundError("Template not found")

        if template.owner_id != user.id and not is_admin(user):
            raise ForbiddenError("Access denied")
        submissions = self.repo.get_submissions(
            template_id=template_id,
            status=status,
            limit=limit,
            offset=offset
        )

        return submissions
