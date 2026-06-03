import hashlib
import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Dict

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.models.enums import SubmissionStatus, TemplateStatus
from app.models.public_link import PublicLink
from app.models.user import User
from app.repositories.template_repository import TemplateRepository
from app.services.placeholder_service import PlaceholderService
from app.services.policy import PolicyService
from app.services.email_services import send_submission_notification

# klase skirta viseo linko kurimui kuris turi vartotojo nuraodyta galiojimo laiko tarpa
class LinkService:
    def __init__(self, db: Session, repo: TemplateRepository | None = None):
        self.db = db
        self.repo = repo or TemplateRepository(db)
# sugeneruojamas hash
    def _generate_hash(self, rendered_content: str, payload: Dict[str, str]) -> str:
        serialized = json.dumps(payload, sort_keys=True)
        base_string = rendered_content + serialized
        return hashlib.sha256(base_string.encode()).hexdigest()

    def _get_valid_link(self, token: str) -> PublicLink:
        link = self.repo.get_public_link_by_token(token)
        if not link:
            raise NotFoundError("Request not found")
# galiojimo laiko nurodymas
        expires_at = link.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at < datetime.now(UTC):
            raise NotFoundError("Request not found")
        return link

    def _resolve_system_prefill(self, system_fields: list[str]) -> Dict[str, str]:
        now = datetime.now(UTC)
        resolved: Dict[str, str] = {}
        for field in system_fields:
            if field == "sys_current_date":
                resolved[field] = now.strftime("%Y-%m-%d")
            elif field == "sys_current_datetime":
                resolved[field] = now.strftime("%Y-%m-%d %H:%M")
        return resolved

    def create_public_link(
        self,
        template_id: int,
        expires_in_hours: int,
        user: User,
        prefill: Dict[str, str] | None = None,
    ) -> PublicLink:
        prefill_data = prefill or {}
        template = self.repo.get_by_id(template_id)
        if not template:
            raise NotFoundError("Template not found")

        PolicyService.check_template_access(user, template)
        if template.status != TemplateStatus.ACTIVE.value:
            raise ForbiddenError("Only active templates can generate public links")

        latest_version = self.repo.get_latest_version(template.id)
        if not latest_version:
            raise NotFoundError("Template version missing")

        placeholders = PlaceholderService.extract_placeholders(latest_version.content)
        owner_fields, system_fields, _ = PlaceholderService.classify_fields(placeholders)
        PlaceholderService.validate_owner_prefill(owner_fields, prefill_data)

        resolved_content = PlaceholderService.render_selected_content(
            latest_version.content,
            {
                **prefill_data,
                **self._resolve_system_prefill(system_fields),
            },
        )

        token = str(uuid.uuid4())
        return self.repo.create_public_link(
            template_id=template.id,
            token=token,
            expires_at=datetime.now(UTC) + timedelta(hours=expires_in_hours),
            resolved_content=resolved_content,
        )
    def list_links_for_template(self, template_id: int, user: User) -> list[PublicLink]:
        template = self.repo.get_by_id(template_id)
        if not template:
            raise NotFoundError("Template not found")
        PolicyService.check_template_access(user, template)
        return self.repo.list_links_for_template(template_id)

    def revoke_public_link(self, link_id: int, user: User) -> PublicLink:
        link = (self.db.query(PublicLink)
                .filter(PublicLink.id == link_id)
                .first()
                )
        if not link:
            raise NotFoundError("Template not found")
        template = (self.repo.get_by_id(link.template_id))
        if not template:
            raise NotFoundError("Template not found")
        PolicyService.check_template_access(user, template)
        return self.repo.revoke_public_link(link_id)
        

    def get_public_template(self, token: str) -> dict[str, str | list[str] | None]:
        link = self._get_valid_link(token)
        template = self.repo.get_by_id(link.template_id)
        if not template or template.status != TemplateStatus.ACTIVE.value:
            raise NotFoundError("Template not found")

        latest_version = self.repo.get_latest_version(template.id)
        if not latest_version:
            raise NotFoundError("Template version missing")

        link_content = link.resolved_content or latest_version.content
        fields = PlaceholderService.extract_placeholders(link_content)
        _, _, public_fields = PlaceholderService.classify_fields(fields)
        return {
            "name": template.name,
            "description": template.description,
            "content": link_content,
            "fields": public_fields,
        }

    def submit_public_contract(
        self,
        token: str,
        payload: Dict[str, str],
        ip: str,
        user_agent: str | None,
        signature_image: str |None,
        submitter_email: str
    ) -> dict[str, str | int]:
        link = self._get_valid_link(token)
        template = self.repo.get_by_id(link.template_id)
        if not template or template.status != TemplateStatus.ACTIVE.value:
            raise NotFoundError("Template not found")

        latest_version = self.repo.get_latest_version(template.id)
        if not latest_version:
            raise NotFoundError("Template version missing")

        link_content = link.resolved_content or latest_version.content
        expected_fields = PlaceholderService.extract_placeholders(link_content)
        _, _, public_fields = PlaceholderService.classify_fields(expected_fields)

        PlaceholderService.validate_payload(public_fields, payload)
        rendered = PlaceholderService.render_content(link_content, payload)
        submission_hash = self._generate_hash(rendered, payload)

        filled = self.repo.create_submission(
            template_id=template.id,
            template_version=latest_version.version_number,
            template_version_id=latest_version.id,
            link_id=link.id,
            submitted_data=payload,
            rendered_content=rendered,
            ip_address=ip,
            user_agent=user_agent,
            signature_image=signature_image,
            submitter_email=submitter_email,
            submission_hash=submission_hash,
            status=SubmissionStatus.SUBMITTED,
        )
        try:
            send_submission_notification(
            owner_email=template.owner.email,
            template_name=template.name,
            submission_id=filled.id
            )
        except Exception:
            pass
            
        return {
            "status": SubmissionStatus.SUBMITTED.value,
            "id": filled.id,
        }

