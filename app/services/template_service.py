import bleach
from bleach.css_sanitizer import CSSSanitizer
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.contract_template import ContractTemplate
from app.models.enums import TemplateStatus
from app.models.user import User
from app.repositories.template_repository import TemplateRepository
from app.schemas.contract_template import ContractTemplateCreate, ContractTemplateUpdate
from app.services.policy import PolicyService

ALLOWED_TAGS = ["b", "i", "u", "s", "br", "p", "ul", "ol", "li", "strong", "h1", "h2", "h3", "em", "blockquote", "span"]
ALLOWED_ATTRIBUTES = {"*": ["style"]}
CSS_SANITIZER = CSSSanitizer(allowed_css_properties=[
    "text-align", "font-weight", "font-style", "text-decoration",
    "color", "font-size", "font-family", "line-height",
    "margin", "margin-top", "margin-bottom", "margin-left", "margin-right",
    "padding", "padding-top", "padding-bottom", "padding-left", "padding-right",
])

def _clean(content: str) -> str:
    return bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, css_sanitizer=CSS_SANITIZER)

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
            content=_clean(payload.content),
            status=TemplateStatus.DRAFT,
        )
        
        self.repo.create_version(
            template_id=template.id,
            version_number=1,
            content=_clean(payload.content),
        )
        return self.repo.save_template(template)

    def duplicate_template(self, template_id: int, user: User) -> ContractTemplate:
        original = self.repo.get_by_id(template_id)
        if not original:
            raise NotFoundError("Template not found")
        PolicyService.check_template_access(user, original)

        latest = self.repo.get_latest_version(original.id)
        content = _clean(latest.content) if latest else _clean(original.content)

        copy = self.repo.create_template(
            owner_id=user.id,
            name=f"Kopija — {original.name}",
            description=original.description,
            content=content,
            status=TemplateStatus.DRAFT,
        )
        self.repo.create_version(template_id=copy.id, version_number=1, content=content)
        return self.repo.save_template(copy)

    def list_user_templates(
        self,
        user: User,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        name: str | None = None,
    ) -> list[ContractTemplate]:
        return self.repo.list_by_owner(user.id, limit=limit, offset=offset, status=status, name=name)


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
            template.content = _clean(payload.content)
        if payload.logo_x is not None:
            template.logo_x = max(0.0, min(88.0, payload.logo_x))
        if payload.logo_y is not None:
            template.logo_y = max(0.0, min(93.0, payload.logo_y))
        if payload.logo_w is not None:
            template.logo_w = max(5.0, min(60.0, payload.logo_w))
        if "client_sig_x" in payload.model_fields_set:
            template.client_sig_x = payload.client_sig_x
            template.client_sig_y = payload.client_sig_y
        if "user_sig_x" in payload.model_fields_set:
            template.user_sig_x = payload.user_sig_x
            template.user_sig_y = payload.user_sig_y

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
