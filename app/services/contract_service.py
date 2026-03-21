from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.contract_template import ContractTemplate
from app.models.filled_contract import FilledContract
from app.models.user import User
from app.services.authorization import is_admin


class ContractService:
    def __init__(self, db: Session):
        self.db = db

    def get_template_submissions(
        self,
        template_id: int,
        user: User,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
    ) -> list[FilledContract]:
        template = (
            self.db.query(ContractTemplate)
            .filter(
                ContractTemplate.id == template_id,
                ContractTemplate.is_deleted == False,
            )
            .first()
        )

        if not template:
            raise NotFoundError("Template not found")

        if template.owner_id != user.id and not is_admin(user):
            raise ForbiddenError("Access denied")

        query = (
            self.db.query(FilledContract)
            .filter(FilledContract.template_id == template_id)
        )

        if status:
            query = query.filter(FilledContract.status == status)

        submissions = (
            query.order_by(FilledContract.submitted_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return submissions
