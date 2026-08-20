import hashlib
import logging
import os
from datetime import datetime, UTC, timedelta

from cryptography.exceptions import InvalidTag
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.enums import SubmissionStatus, TemplateStatus
from app.models.submission import Submission
from app.models.signing_audit_trail import SigningAuditTrail
from app.models.user import User
from app.repositories.template_repository import TemplateRepository
from app.repositories.user_profile_repository import UserProfileRepository
from app.renderers.document_renderer import render_contract_html
from app.renderers.pdf_renderer import render_pdf_from_html
from app.services.code_service import CodeService
from app.services.encryption_service import EncryptionService
from app.services.placeholder_service import PlaceholderService
from app.services.policy import PolicyService

logger = logging.getLogger(__name__)

APP_URL = os.getenv("APP_URL", "https://melno.app")

_SENSITIVE_SIGN_ENDPOINTS = {"/signing/submissions"}


class SubmissionService:
    def __init__(self, db: Session, repo: TemplateRepository | None = None):
        self.db = db
        self.repo = repo or TemplateRepository(db)

    # ------------------------------------------------------------------
    # Create submission
    # ------------------------------------------------------------------

    def create_submission(
        self,
        *,
        template_id: int,
        expires_in_hours: int,
        user: User,
        prefill: dict[str, str] | None = None,
        recipient_email: str | None = None,
    ) -> dict:
        prefill_data = prefill or {}
        template = self.repo.get_active_by_id(template_id)
        if not template:
            raise NotFoundError("Template not found")

        PolicyService.check_template_access(user, template)

        latest_version = self.repo.get_latest_version(template.id)
        if not latest_version:
            raise NotFoundError("Template version missing")

        placeholders = PlaceholderService.extract_placeholders(latest_version.content)
        owner_fields, system_fields, _ = PlaceholderService.classify_fields(placeholders)
        PlaceholderService.validate_owner_prefill(owner_fields, prefill_data)

        system_resolved = self._resolve_system_fields(system_fields)
        resolved_content = PlaceholderService.render_selected_content(
            latest_version.content,
            {**prefill_data, **system_resolved},
        )

        is_sensitive = PlaceholderService.has_sensitive_fields(resolved_content)

        access_code_plain, access_code_hash = CodeService.generate()

        submission = Submission(
            template_id=template.id,
            template_version_id=latest_version.id,
            creator_id=user.id,
            recipient_email=recipient_email,
            is_sensitive=is_sensitive,
            resolved_content=resolved_content,
            access_code_hash=access_code_hash,
            status=SubmissionStatus.PENDING,
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(hours=expires_in_hours),
            logo_x=str(template.logo_x) if template.logo_x is not None else "5.0",
            logo_y=str(template.logo_y) if template.logo_y is not None else "5.0",
            logo_w=str(template.logo_w) if template.logo_w is not None else "15.0",
            client_sig_x=str(template.client_sig_x) if template.client_sig_x is not None else None,
            client_sig_y=str(template.client_sig_y) if template.client_sig_y is not None else None,
            user_sig_x=str(template.user_sig_x) if template.user_sig_x is not None else None,
            user_sig_y=str(template.user_sig_y) if template.user_sig_y is not None else None,
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)

        signing_url = f"{APP_URL}/sign/{submission.uuid}"

        if recipient_email:
            try:
                from app.services.email_services import send_signing_invitation
                send_signing_invitation(
                    recipient_email=recipient_email,
                    template_name=template.name,
                    signing_url=signing_url,
                    access_code=access_code_plain,
                    expires_at=submission.expires_at,
                )
            except Exception:
                logger.exception("Failed to send signing invitation for submission %s", submission.uuid)
            return {
                "uuid": submission.uuid,
                "expires_at": submission.expires_at,
                "email_sent": True,
            }

        return {
            "uuid": submission.uuid,
            "access_code": access_code_plain,
            "expires_at": submission.expires_at,
            "email_sent": False,
        }

    # ------------------------------------------------------------------
    # Get metadata (public, no auth)
    # ------------------------------------------------------------------

    def get_submission_meta(self, uuid: str) -> dict:
        sub = self._get_valid_submission(uuid)
        template = self.repo.get_by_id(sub.template_id)
        return {
            "uuid": sub.uuid,
            "template_name": template.name if template else "",
            "description": template.description if template else "",
            "is_sensitive": sub.is_sensitive,
            "status": sub.status,
            "expires_at": sub.expires_at,
        }

    # ------------------------------------------------------------------
    # Verify access code
    # ------------------------------------------------------------------

    def verify_access_code(self, uuid: str, code: str) -> datetime:
        """
        Verify the recipient's access code.
        Returns code_verified_at timestamp on success.
        Raises BadRequestError on invalid or locked.
        """
        sub = self._get_valid_submission(uuid)

        if CodeService.is_locked(sub.access_locked_until):
            raise BadRequestError("Too many attempts. Try again later.")

        if not CodeService.verify(code, sub.access_code_hash):
            sub.access_attempts += 1
            sub.access_locked_until = CodeService.next_locked_until(sub.access_attempts)
            self.db.commit()
            remaining = max(0, 5 - sub.access_attempts)
            raise BadRequestError(f"Invalid code. {remaining} attempt(s) remaining.")

        # Reset attempt counter on success
        sub.access_attempts = 0
        sub.access_locked_until = None
        self.db.commit()

        return datetime.now(UTC)

    # ------------------------------------------------------------------
    # Get preview (post code verification)
    # ------------------------------------------------------------------

    def get_preview(self, uuid: str) -> dict:
        sub = self._get_valid_submission(uuid)
        template = self.repo.get_by_id(sub.template_id)

        content = sub.resolved_content or ""
        placeholders = PlaceholderService.extract_placeholders(content)
        _, _, public_fields = PlaceholderService.classify_fields(placeholders)

        profile_repo = UserProfileRepository(self.db)
        owner_profile = profile_repo.get_by_user_id(sub.creator_id)
        logo_image = owner_profile.logo_image if owner_profile else None

        return {
            "uuid": sub.uuid,
            "template_name": template.name if template else "",
            "content": content,
            "fields": public_fields,
            "is_sensitive": sub.is_sensitive,
            "logo_image": logo_image,
            "logo_x": float(sub.logo_x) if sub.logo_x else 5.0,
            "logo_y": float(sub.logo_y) if sub.logo_y else 5.0,
            "logo_w": float(sub.logo_w) if sub.logo_w else 15.0,
        }

    # ------------------------------------------------------------------
    # Record that client viewed the contract
    # ------------------------------------------------------------------

    def record_contract_viewed(self, uuid: str) -> None:
        sub = self.db.query(Submission).filter(Submission.uuid == uuid).first()
        if sub and sub.audit_trail:
            if sub.audit_trail.contract_viewed_at is None:
                sub.audit_trail.contract_viewed_at = datetime.now(UTC)
                self.db.commit()

    # ------------------------------------------------------------------
    # Decline
    # ------------------------------------------------------------------

    def decline(self, uuid: str, ip: str) -> dict:
        sub = self._get_valid_submission(uuid)
        template = self.repo.get_by_id(sub.template_id)

        sub.status = SubmissionStatus.DECLINED
        self.db.commit()

        try:
            from app.services.email_services import send_contract_declined
            if template and template.owner:
                send_contract_declined(
                    owner_email=template.owner.email,
                    template_name=template.name,
                )
        except Exception:
            logger.exception("Failed to send decline notification for submission %s", uuid)

        return {"status": "declined"}

    # ------------------------------------------------------------------
    # Sign (core — RAM only rendering, AES encryption, audit trail)
    # ------------------------------------------------------------------

    def sign(
        self,
        *,
        uuid: str,
        payload: dict[str, str],
        signature_image: str | None,
        signer_full_name: str,
        confirmed_read: bool,
        confirmed_esign: bool,
        ip: str,
        user_agent: str | None,
        browser_language: str | None,
        timezone: str | None,
        screen_resolution: str | None,
        code_verified_at: datetime,
        contract_viewed_at: datetime | None,
    ) -> bytes:
        """
        Render contract in RAM, encrypt for owner, write audit trail, return PDF bytes.
        Personal data in `payload` is NEVER written to the database.
        """
        sub = self._get_valid_submission(uuid)
        template = self.repo.get_by_id(sub.template_id)
        if not template:
            raise NotFoundError("Template not found")

        if not confirmed_read or not confirmed_esign:
            raise BadRequestError("Both consent checkboxes must be confirmed.")

        content = sub.resolved_content or ""
        placeholders = PlaceholderService.extract_placeholders(content)
        _, _, public_fields = PlaceholderService.classify_fields(placeholders)
        PlaceholderService.validate_payload(public_fields, payload)

        # --- Render in RAM — payload never leaves this scope ---
        rendered_html_content = PlaceholderService.render_content(content, payload)

        document_hash = hashlib.sha256(rendered_html_content.encode()).hexdigest()

        profile_repo = UserProfileRepository(self.db)
        owner_profile = profile_repo.get_by_user_id(sub.creator_id)
        user_signature_image = owner_profile.signature_image if owner_profile else None
        logo_image = owner_profile.logo_image if owner_profile else None

        signer_name_from_payload = (
            payload.get("client_name")
            or payload.get("client_vardas")
            or signer_full_name
        )

        full_html = render_contract_html(
            content=rendered_html_content,
            signature_image=signature_image,
            signer_name=signer_name_from_payload,
            user_signature_image=user_signature_image,
            logo_image=logo_image,
            logo_x=float(sub.logo_x) if sub.logo_x else 5.0,
            logo_y=float(sub.logo_y) if sub.logo_y else 5.0,
            logo_w=float(sub.logo_w) if sub.logo_w else 15.0,
            client_sig_x=float(sub.client_sig_x) if sub.client_sig_x else None,
            client_sig_y=float(sub.client_sig_y) if sub.client_sig_y else None,
            user_sig_x=float(sub.user_sig_x) if sub.user_sig_x else None,
            user_sig_y=float(sub.user_sig_y) if sub.user_sig_y else None,
        )

        # Render PDF in RAM
        pdf_bytes = render_pdf_from_html(full_html)

        # Encrypt for owner download
        aes_key = EncryptionService.generate_key()
        encrypted_blob, nonce = EncryptionService.encrypt(pdf_bytes, aes_key)
        key_b64 = EncryptionService.key_to_url_safe(aes_key)
        del aes_key  # key no longer needed in memory

        # Generate owner download code
        owner_code_plain, owner_code_hash = CodeService.generate()

        now = datetime.now(UTC)
        signed_at = now

        # Write audit trail (no personal data, no payload values)
        audit = SigningAuditTrail(
            submission_uuid=uuid,
            document_hash=document_hash,
            recipient_email=sub.recipient_email,
            recipient_ip=ip,
            user_agent=user_agent,
            browser_language=browser_language,
            timezone=timezone,
            screen_resolution=screen_resolution,
            signer_full_name=signer_full_name,
            confirmed_read=confirmed_read,
            confirmed_esign=confirmed_esign,
            code_verified_at=code_verified_at,
            contract_viewed_at=contract_viewed_at,
            signed_at=signed_at,
            creator_id=sub.creator_id,
            creator_ip=None,
            created_at=now,
        )
        self.db.add(audit)

        # Store encrypted blob and owner code hash; wipe access code
        sub.encrypted_pdf_blob = encrypted_blob
        sub.encryption_nonce = nonce
        sub.owner_download_code_hash = owner_code_hash
        sub.signature_image = signature_image
        sub.status = SubmissionStatus.SIGNED
        sub.signed_at = signed_at
        sub.access_code_hash = ""  # invalidate access code after signing
        self.db.commit()

        # Notify owner
        download_url = f"{APP_URL}/download/owner/{uuid}?k={key_b64}"
        try:
            from app.services.email_services import send_owner_signed_notification
            send_owner_signed_notification(
                owner_email=template.owner.email,
                template_name=template.name,
                download_url=download_url,
                download_code=owner_code_plain,
            )
        except Exception:
            logger.exception("Failed to send owner notification for submission %s", uuid)

        # Clear rendered content from memory (Python GC will handle it, but signal intent)
        del rendered_html_content, full_html

        return pdf_bytes

    # ------------------------------------------------------------------
    # Owner download (one-time)
    # ------------------------------------------------------------------

    def owner_download(self, uuid: str, code: str, aes_key_b64: str, owner: User) -> bytes:
        sub = self.db.query(Submission).filter(Submission.uuid == uuid).first()
        if not sub:
            raise NotFoundError("Submission not found")

        if sub.creator_id != owner.id:
            raise ForbiddenError("Access denied")

        if sub.status != SubmissionStatus.SIGNED:
            raise BadRequestError("Submission is not available for download")

        if CodeService.is_locked(sub.owner_download_locked_until):
            raise BadRequestError("Too many attempts. Try again later.")

        if not CodeService.verify(code, sub.owner_download_code_hash):
            sub.owner_download_attempts += 1
            sub.owner_download_locked_until = CodeService.next_locked_until(
                sub.owner_download_attempts
            )
            self.db.commit()
            remaining = max(0, 5 - sub.owner_download_attempts)
            raise BadRequestError(f"Invalid code. {remaining} attempt(s) remaining.")

        try:
            aes_key = EncryptionService.key_from_url_safe(aes_key_b64)
            pdf_bytes = EncryptionService.decrypt(
                sub.encrypted_pdf_blob, sub.encryption_nonce, aes_key
            )
            del aes_key
        except (InvalidTag, Exception):
            raise BadRequestError("Invalid or corrupted download link.")

        # Wipe blob and invalidate — one-time download
        sub.encrypted_pdf_blob = None
        sub.encryption_nonce = None
        sub.owner_download_code_hash = None
        sub.status = SubmissionStatus.COMPLETED
        sub.downloaded_at = datetime.now(UTC)
        self.db.commit()

        return pdf_bytes

    # ------------------------------------------------------------------
    # List submissions for owner (dashboard)
    # ------------------------------------------------------------------

    def list_for_owner(self, owner: User) -> list[dict]:
        subs = (
            self.db.query(Submission)
            .filter(Submission.creator_id == owner.id)
            .order_by(Submission.created_at.desc())
            .all()
        )
        return [
            {
                "uuid": s.uuid,
                "template_id": s.template_id,
                "template_name": s.template.name if s.template else "",
                "recipient_email": s.recipient_email,
                "status": s.status,
                "is_sensitive": s.is_sensitive,
                "created_at": s.created_at,
                "expires_at": s.expires_at,
                "signed_at": s.signed_at,
            }
            for s in subs
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_valid_submission(self, uuid: str) -> Submission:
        sub = self.db.query(Submission).filter(Submission.uuid == uuid).first()
        if not sub:
            raise NotFoundError("Submission not found")
        expires_at = sub.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at < datetime.now(UTC):
            raise NotFoundError("Submission not found")
        if sub.status not in (SubmissionStatus.PENDING, SubmissionStatus.SIGNED):
            raise NotFoundError("Submission not found")
        return sub

    @staticmethod
    def _resolve_system_fields(system_fields: list[str]) -> dict[str, str]:
        now = datetime.now(UTC)
        resolved: dict[str, str] = {}
        for field in system_fields:
            if field == "sys_current_date":
                resolved[field] = now.strftime("%Y-%m-%d")
            elif field == "sys_current_datetime":
                resolved[field] = now.strftime("%Y-%m-%d %H:%M")
        return resolved
