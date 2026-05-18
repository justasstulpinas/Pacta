import bleach
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.contract_template import ContractTemplate
from app.models.enums import TemplateStatus
from app.models.user import User
from app.repositories.template_repository import TemplateRepository
from app.schemas.contract_template import ContractTemplateCreate, ContractTemplateUpdate
from app.services.policy import PolicyService

# sablono sukurimo klase 
class TemplateService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TemplateRepository(db)

    def create_template(
        self,
        payload: ContractTemplateCreate,
        user: User,
    ) -> ContractTemplate:
        template = self.repo.create_template(
            owner_id=user.id,
            name=payload.name,
            description=payload.description,
            content=bleach.clean(payload.content, tags=["b", "i", "u", "br", "p", "ul", "ol", "li", "strong", "h1", "h2", "h3", "em"]),
            status=TemplateStatus.DRAFT,
        )
        
        self.repo.create_version(
            template_id=template.id,
            version_number=1,
            content=bleach.clean(payload.content, tags=["b", "i", "u", "br", "p", "ul", "ol", "li", "strong", "h1", "h2", "h3", "em"]),
        )
        return self.repo.save_template(template)

    def list_user_templates(self, user: User) -> list[ContractTemplate]:
        return self.repo.list_by_owner(user.id)

    def get_template_by_id(
        self,
        template_id: int,
        user: User,
    ) -> ContractTemplate:
        template = self.repo.get_by_id(template_id)
        if not template:
            raise NotFoundError("Template not found")
        PolicyService.check_template_access(user, template)
        return template

    def update_template(
        self,
        template_id: int,
        payload: ContractTemplateUpdate,
        user: User,
    ) -> ContractTemplate:
        template = self.repo.get_by_id(template_id)
        if not template:
            raise NotFoundError("Template not found")
        PolicyService.check_template_access(user, template)

        if template.status == TemplateStatus.ARCHIVED.value:
            raise ForbiddenError("Archived templates cannot be edited")

        content_changed = False
        if payload.name is not None:
            template.name = payload.name
        if payload.description is not None:
            template.description = payload.description
        if payload.content is not None and payload.content != template.content:
            content_changed = True
            template.content = bleach.clean(payload.content, tags=["b", "i", "u", "br", "p", "ul", "ol", "li", "strong", "h1", "h2", "h3", "em"])

        if content_changed:
            latest_version = self.repo.get_latest_version(template.id)
            next_version = 1 if not latest_version else latest_version.version_number + 1
            self.repo.create_version(
                template_id=template.id,
                version_number=next_version,
                content=template.content,
            )

        template.updated_at = datetime.now(UTC)
        return self.repo.save_template(template)

    def activate_template(
        self,
        template_id: int,
        user: User,
    ) -> ContractTemplate:
        template = self.repo.get_by_id(template_id)
        if not template:
            raise NotFoundError("Template not found")
        PolicyService.check_template_access(user, template)

        if template.status != TemplateStatus.DRAFT.value:
            raise ForbiddenError("Only draft templates can be activated")

        template.status = TemplateStatus.ACTIVE.value
        template.updated_at = datetime.now(UTC)
        return self.repo.save_template(template)

    def archive_template(
        self,
        template_id: int,
        user: User,
    ) -> ContractTemplate:
        template = self.repo.get_by_id(template_id)
        if not template:
            raise NotFoundError("Template not found")
        PolicyService.check_template_access(user, template)

        if template.status != TemplateStatus.ACTIVE.value:
            raise ForbiddenError("Only active templates can be archived")

        template.status = TemplateStatus.ARCHIVED.value
        template.updated_at = datetime.now(UTC)
        return self.repo.save_template(template)

    def soft_delete_template(
        self,
        template_id: int,
        user: User,
    ) -> ContractTemplate:
        template = self.repo.get_by_id(template_id)
        if not template:
            raise NotFoundError("Template not found")
        PolicyService.check_template_access(user, template)

        if template.status == TemplateStatus.ACTIVE.value:
            raise ForbiddenError("Active templates cannot be deleted")

        template.is_deleted = True
        template.updated_at = datetime.now(UTC)
        return self.repo.save_template(template)
