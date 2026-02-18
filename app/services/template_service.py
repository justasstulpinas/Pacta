from sqlalchemy.orm import Session

from app.services.authorization import is_admin
from app.services.ownership import require_ownership
from app.models.contract_template import ContractTemplate
from app.models.user import User
from app.core.exceptions import NotFoundError, ForbiddenError
from app.services.authorization import is_admin


class TemplateService:
    def __init__(self, db: Session):
        self.db = db
    def get_template_by_id(self, template_id: int, user: User):
        template = (
            self.db.query(ContractTemplate)
            .filter(
                ContractTemplate.id == template_id,
                ContractTemplate.is_deleted == False
                )
            .first()
        )

        if not template or template.is_deleted:
            raise NotFoundError("Template not found")
        if template.owner_id != user.id and not is_admin(user):
            raise ForbiddenError("Access denied")
        return template
