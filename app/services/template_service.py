from datetime import datetime
from sqlalchemy.orm import Session

from app.models.contract_template import ContractTemplate
from app.models.contract_template_versions import ContractTemplateVersion
from app.models.user import User
from app.schemas.contract_template import (
    ContractTemplateCreate,
    ContractTemplateUpdate,
)
from app.services.authorization import is_admin
from app.core.exceptions import NotFoundError, ForbiddenError


class TemplateService:
    def __init__(self, db: Session):
        self.db = db

    def create_template(
        self,
        payload: ContractTemplateCreate,
        user: User,
    ) -> ContractTemplate:

        template = ContractTemplate(
            owner_id=user.id,
            name=payload.name,
            description=payload.description,  # FIXED typo
            content=payload.content,
            status="draft",
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
        return (
            self.db.query(ContractTemplate)
            .filter(
                ContractTemplate.owner_id == user.id,
                ContractTemplate.is_deleted == False,
            )
            .all()
        )

    def get_template_by_id(
        self,
        template_id: int,
        user: User,
    ) -> ContractTemplate:

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

        return template

    def update_template(
        self,
        template_id: int,
        payload: ContractTemplateUpdate,
        user: User,
    ) -> ContractTemplate:

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

        if template.status != "draft":
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
            latest_version = (
                self.db.query(ContractTemplateVersion)
                .filter(ContractTemplateVersion.template_id == template.id)
                .order_by(ContractTemplateVersion.version_number.desc())
                .first()
            )

            next_version = 1 if not latest_version else latest_version.version_number + 1

            new_version = ContractTemplateVersion(
                template_id=template.id,
                version_number=next_version,
                content=template.content,  # FIXED field
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

        if template.status != "draft":
            raise ForbiddenError("Only draft templates can be activated")

        template.status = "active"
        template.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(template)

        return template

    def archive_template(
        self,
        template_id: int,
        user: User,
    ) -> ContractTemplate:

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

        if template.status != "active":
            raise ForbiddenError("Only active templates can be archived")

        template.status = "archived"
        template.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(template)

        return template

    def soft_delete_template(
        self,
        template_id: int,
        user: User,
    ) -> ContractTemplate:

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

        if template.status == "active":
            raise ForbiddenError("Active templates cannot be deleted")

        template.is_deleted = True
        template.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(template)

        return template