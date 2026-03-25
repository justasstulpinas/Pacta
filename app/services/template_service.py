from datetime import datetime
from sqlalchemy.orm import Session

from app.models.contract_template import ContractTemplate
from app.models.contract_template_versions import ContractTemplateVersion
from app.models.user import User
from app.models.enums import ContractTemplateStatus

from app.schemas.contract_template import (
    ContractTemplateCreate,
    ContractTemplateUpdate,
)

from app.services.policy import require_owner_or_admin

from app.core.exceptions import NotFoundError, ForbiddenError

from app.repositories.template_repository import TemplateRepository


class TemplateService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TemplateRepository(db)

    def _get_template(self, template_id: int) -> ContractTemplate:
        template = self.repo.get_active_by_id(template_id)

        if not template:
            raise NotFoundError("Template not found")

        return template

    def create_template(
        self,
        payload: ContractTemplateCreate,
        user: User,
    ) -> ContractTemplate:

        template = ContractTemplate(
            owner_id=user.id,
            name=payload.name,
            description=payload.description,
            content=payload.content,
            status=ContractTemplateStatus.DRAFT.value,
        )

        self.db.add(template)
        self.db.flush()

        version = ContractTemplateVersion(
            template_id=template.id,
            version_number=1,
            content=payload.content,
        )

        self.db.add(version)
        self.db.commit()
        self.db.refresh(template)

        return template

    def list_user_templates(self, user: User):
        return self.repo.list_by_owner(user.id)

    def get_template_by_id(
        self,
        template_id: int,
        user: User,
    ) -> ContractTemplate:

        template = self._get_template(template_id)

        require_owner_or_admin(template.owner_id, user)

        return template

    def update_template(
        self,
        template_id: int,
        payload: ContractTemplateUpdate,
        user: User,
    ) -> ContractTemplate:

        template = self._get_template(template_id)

        require_owner_or_admin(template.owner_id, user)

        if template.status != ContractTemplateStatus.DRAFT.value:
            raise ForbiddenError("Only draft templates can be edited")

        content_changed = False

        if payload.name is not None:
            template.name = payload.name

        if payload.description is not None:
            template.description = payload.description

        if payload.content is not None and payload.content != template.content:
            content_changed = True
            template.content = payload.content

        if content_changed:
            latest_version = self.repo.get_latest_version(template.id)

            next_version = (
                1 if not latest_version else latest_version.version_number + 1
            )

            new_version = ContractTemplateVersion(
                template_id=template.id,
                version_number=next_version,
                content=template.content,
            )

            self.db.add(new_version)

        template.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(template)

        return template

    def activate_template(
        self,
        template_id: int,
        user: User,
    ) -> ContractTemplate:

        template = self._get_template(template_id)

        require_owner_or_admin(template.owner_id, user)

        if template.status != ContractTemplateStatus.DRAFT.value:
            raise ForbiddenError("Only draft templates can be activated")

        template.status = ContractTemplateStatus.ACTIVE.value
        template.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(template)

        return template

    def archive_template(
        self,
        template_id: int,
        user: User,
    ) -> ContractTemplate:

        template = self._get_template(template_id)

        require_owner_or_admin(template.owner_id, user)

        if template.status != ContractTemplateStatus.ACTIVE.value:
            raise ForbiddenError("Only active templates can be archived")

        template.status = ContractTemplateStatus.ARCHIVED.value
        template.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(template)

        return template

    def soft_delete_template(
        self,
        template_id: int,
        user: User,
    ) -> ContractTemplate:

        template = self._get_template(template_id)

        require_owner_or_admin(template.owner_id, user)

        if template.status == ContractTemplateStatus.ACTIVE.value:
            raise ForbiddenError("Active templates cannot be deleted")

        template.is_deleted = True
        template.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(template)

        return template