import uuid
import hashlib
import json
from typing import Dict
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session

from app.models.public_link import PublicLink
from app.models.contract_template import ContractTemplate
from app.models.contract_template_versions import ContractTemplateVersion
from app.models.filled_contract import FilledContract
from app.models.user import User

from app.models.enums import ContractTemplateStatus

from app.services.placeholder_service import PlaceholderService

from app.services.policy import require_owner_or_admin

from app.core.exceptions import NotFoundError, ForbiddenError

from app.repositories.template_repository import TemplateRepository 


class LinkService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TemplateRepository(db)


    def _generate_hash(self, rendered_content: str, payload: Dict[str, str]) -> str:
        serialized = json.dumps(payload, sort_keys=True)
        base_string = rendered_content + serialized
        return hashlib.sha256(base_string.encode()).hexdigest()

    def _get_valid_public_link(self, token: str) -> PublicLink:
        link = self.repo.get_valid_link(token)  

        if not link:
            raise NotFoundError("Request not found")
        
        expires_at = link.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)

        if expires_at < datetime.now(UTC):
            raise NotFoundError("Request not found")    
        return link

    def _get_active_template(self, template_id: int) -> ContractTemplate:
        template = self.repo.get_active_template_for_public(template_id)

        if not template:
            raise NotFoundError("Template not found")

        return template

    def _get_latest_version(self, template_id: int) -> ContractTemplateVersion:
        version = self.repo.get_latest_version(template_id)

        if not version:
            raise NotFoundError("Template version missing")

        return version

    def create_public_link(
        self,
        template_id: int,
        expires_in_hours: int,
        user: User,
    ) -> PublicLink:

        template = self.repo.get_active_by_id(template_id)

        if not template:
            raise NotFoundError("Template not found")

        require_owner_or_admin(template.owner_id, user)

        if template.status != ContractTemplateStatus.ACTIVE.value:
            raise ForbiddenError(
                "Only active templates can generate public links"
            )

        token = str(uuid.uuid4())

        link = PublicLink(
            template_id=template.id,
            token=token,
            expires_at=datetime.now(UTC) + timedelta(hours=expires_in_hours),
        )

        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)

        return link

    def get_public_template(self, token: str):
        link = self._get_valid_public_link(token)
        template = self._get_active_template(link.template_id)

        latest_version = self.repo._get_latest_version(template.id)

        fields = PlaceholderService.extract_placeholders(
            latest_version.content
        )

        return {
            "name": template.name,
            "description": template.description,
            "content": latest_version.content,
            "fields": fields,
        }

    def submit_public_contract(
        self,
        token: str,
        payload: Dict[str, str],
        ip: str,
        user_agent: str | None,
    ):
        link = self._get_valid_public_link(token)
        template = self._get_active_template(link.template_id)

        latest_version = self._get_latest_version(template.id)

        expected_fields = PlaceholderService.extract_placeholders(
            latest_version.content
        )

        PlaceholderService.validate_payload(expected_fields, payload)

        rendered = PlaceholderService.render_content(
            latest_version.content,
            payload,
        )

        submission_hash = self._generate_hash(rendered, payload)

        filled = FilledContract(
            template_id=template.id,
            template_version=latest_version.version_number,
            template_version_id=latest_version.id,
            link_id=link.id,
            submitted_data=payload,
            rendered_content=rendered,
            ip_address=ip,
            user_agent=user_agent,
            submission_hash=submission_hash,
            status="submitted",
        )

        self.db.add(filled)
        self.db.commit()
        self.db.refresh(filled)

        return {
            "status": "submitted",
            "id": filled.id,
        }