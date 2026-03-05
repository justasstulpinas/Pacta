import uuid
import hashlib
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.public_link import PublicLink
from app.models.contract_template import ContractTemplate
from app.models.filled_contract import FilledContract
from app.models.user import User
from app.services.authorization import is_admin
from app.services.placeholder_service import PlaceholderService
from app.core.exceptions import NotFoundError, ForbiddenError


class LinkService:
    def __init__(self, db: Session):
        self.db = db


    def _generate_hash(self, rendered_content: str, payload: dict) -> str:
        serialized = json.dumps(payload, sort_keys=True)
        base_string = rendered_content + serialized
        return hashlib.sha256(base_string.encode()).hexdigest()

    def _get_valid_public_link(self, token: str) -> PublicLink:
        link = (
            self.db.query(PublicLink)
            .filter(
                PublicLink.token == token,
                PublicLink.is_revoked == False,
            )
            .first()
        )

        if not link:
            raise NotFoundError("Request not found")

        if link.expires_at <= datetime.utcnow():
            raise NotFoundError("Request not found")

        return link

    def _get_active_template(self, template_id: int) -> ContractTemplate:
        template = (
            self.db.query(ContractTemplate)
            .filter(
                ContractTemplate.id == template_id,
                ContractTemplate.is_deleted == False,
                ContractTemplate.status == "active",
            )
            .first()
        )

        if not template:
            raise NotFoundError("Request not found")

        return template

    def create_public_link(
        self,
        template_id: int,
        expires_in_hours: int,
        user: User,
    ) -> PublicLink:

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
            raise ForbiddenError(
                "Only active templates can generate public links"
            )

        token = str(uuid.uuid4())

        link = PublicLink(
            template_id=template.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
        )

        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)

        return link

    def get_public_template(self, token: str):
        link = self._get_valid_public_link(token)
        template = self._get_active_template(link.template_id)

        fields = PlaceholderService.extract_placeholders(
            template.content
        )

        return {
            "name": template.name,
            "description": template.description,
            "content": template.content,
            "fields": fields,
        }


    def submit_public_contract(
        self,
        token: str,
        payload: dict,
        ip: str,
        user_agent: str | None,
    ):
        link = self._get_valid_public_link(token)
        template = self._get_active_template(link.template_id)

        expected_fields = PlaceholderService.extract_placeholders(
            template.content
        )

        PlaceholderService.validate_payload(expected_fields, payload)

        rendered = PlaceholderService.render_content(
            template.content,
            payload,
        )

        submission_hash = self._generate_hash(rendered, payload)

        filled = FilledContract(
            template_id=template.id,
            link_id=link.id,
            submitted_data=payload,
            rendered_content=rendered,
            ip_address=ip,
            user_agent=user_agent,
            submission_hash=submission_hash,
        )

        self.db.add(filled)
        self.db.commit()
        self.db.refresh(filled)

        return {
            "status": "submitted",
            "id": filled.id,
        }