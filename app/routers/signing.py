import logging
from datetime import datetime, UTC
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.limiter import limiter
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.submission_service import SubmissionService
from app.core.security import create_signed_token, decode_token
from app.core.exceptions import UnauthorizedError, BadRequestError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/signing", tags=["signing"])

# ------------------------------------------------------------------
# Session cookie helpers (short-lived, scoped to one submission)
# ------------------------------------------------------------------

_SESSION_COOKIE = "signing_session"
_SESSION_TTL_MINUTES = 30


def _issue_session_cookie(response: Response, uuid: str, code_verified_at: datetime) -> None:
    token = create_signed_token(
        data={
            "sub": uuid,
            "purpose": "signing_session",
            "verified_at": code_verified_at.isoformat(),
        },
        expires_minutes=_SESSION_TTL_MINUTES,
    )
    import os
    is_prod = os.getenv("ENVIRONMENT") == "production"
    response.set_cookie(
        key=_SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="strict" if is_prod else "lax",
        max_age=_SESSION_TTL_MINUTES * 60,
        path=f"/signing/submissions/{uuid}",
    )


def _require_session(uuid: str, signing_session: str | None = Cookie(default=None)) -> dict:
    if not signing_session:
        raise UnauthorizedError("Signing session required")
    payload = decode_token(signing_session)
    if not payload or payload.get("purpose") != "signing_session":
        raise UnauthorizedError("Invalid signing session")
    if payload.get("sub") != uuid:
        raise UnauthorizedError("Session does not match this submission")
    return payload


# ------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------

class CreateSubmissionRequest(BaseModel):
    template_id: int
    expires_in_hours: int = 72
    prefill: dict[str, str] | None = None
    recipient_email: EmailStr | None = None


class VerifyCodeRequest(BaseModel):
    code: str


class SignRequest(BaseModel):
    payload: dict[str, str]
    signature_image: str | None = None
    signer_full_name: str
    confirmed_read: bool
    confirmed_esign: bool
    browser_language: str | None = None
    timezone: str | None = None
    screen_resolution: str | None = None
    contract_viewed_at: str | None = None  # ISO datetime string from client


class OwnerDownloadRequest(BaseModel):
    code: str


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------

@router.post("/submissions")
def create_submission(
    body: CreateSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new secure submission. Generates a UUID4 identifier and 6-digit access code.
    If recipient_email is provided, the system emails the code to the client directly.
    Otherwise returns the code for the owner to share manually.
    """
    service = SubmissionService(db)
    return service.create_submission(
        template_id=body.template_id,
        expires_in_hours=body.expires_in_hours,
        user=current_user,
        prefill=body.prefill,
        recipient_email=body.recipient_email,
    )


@router.get("/submissions")
def list_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all submissions created by the authenticated owner."""
    service = SubmissionService(db)
    return service.list_for_owner(current_user)


@router.get("/submissions/{uuid}")
def get_submission_meta(uuid: str, db: Session = Depends(get_db)):
    """
    Public endpoint — return submission metadata (template name, status, sensitivity flag).
    No contract content is returned here.
    """
    service = SubmissionService(db)
    return service.get_submission_meta(uuid)


@router.post("/submissions/{uuid}/verify-code")
@limiter.limit("5/minute")
def verify_code(
    uuid: str,
    body: VerifyCodeRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Verify the recipient's 6-digit access code.
    On success: issues a short-lived HttpOnly session cookie scoped to this submission.
    Rate limited to 5 attempts/minute per IP.
    """
    service = SubmissionService(db)
    code_verified_at = service.verify_access_code(uuid, body.code)
    _issue_session_cookie(response, uuid, code_verified_at)
    return {"verified": True}


@router.get("/submissions/{uuid}/preview")
def get_preview(
    uuid: str,
    db: Session = Depends(get_db),
    signing_session: str | None = Cookie(default=None),
):
    """
    Return the resolved template HTML for the client to preview.
    Requires a valid signing session cookie (i.e. code already verified).
    No client fields are pre-filled — only owner/system placeholders resolved.
    Request body is not logged.
    """
    _require_session(uuid, signing_session)
    service = SubmissionService(db)
    return service.get_preview(uuid)


@router.get("/submissions/{uuid}/preview-docx")
def get_preview_docx(
    uuid: str,
    db: Session = Depends(get_db),
    signing_session: str | None = Cookie(default=None),
):
    """Return partially-filled DOCX for preview: owner+system fields filled, client placeholders intact."""
    from fastapi.responses import Response as FastResponse
    import json as _json
    from app.models.submission import Submission
    from app.renderers.docx_filler import fill_docx_placeholders
    from app.services.template_service import DOCX_UPLOAD_DIR
    from app.repositories.template_repository import TemplateRepository
    from datetime import datetime, UTC

    _require_session(uuid, signing_session)

    sub = db.query(Submission).filter(Submission.uuid == uuid).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Not found")

    content = sub.resolved_content or ""
    try:
        meta = _json.loads(content)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Not a DOCX submission")

    if meta.get("type") != "docx":
        raise HTTPException(status_code=400, detail="Not a DOCX submission")

    repo = TemplateRepository(db)
    template = repo.get_by_id(sub.template_id)
    if not template or not template.docx_path:
        raise HTTPException(status_code=404, detail="Template not found")

    docx_path = DOCX_UPLOAD_DIR / template.docx_path
    if not docx_path.exists():
        raise HTTPException(status_code=404, detail="DOCX file not found")

    # Fill only owner + system fields; leave client fields as {{placeholder}}
    owner_prefill = meta.get("owner_prefill", {})
    system_fields_list = meta.get("system_fields", [])
    now = datetime.now(UTC)
    system_resolved = {
        f: now.strftime("%Y-%m-%d") if f == "sys_current_date" else now.strftime("%Y-%m-%d %H:%M")
        for f in system_fields_list
    }
    values = {**owner_prefill, **system_resolved}

    filled = fill_docx_placeholders(docx_path.read_bytes(), values)
    return FastResponse(
        content=filled,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.post("/submissions/{uuid}/viewed")
def mark_viewed(
    uuid: str,
    db: Session = Depends(get_db),
    signing_session: str | None = Cookie(default=None),
):
    """Record that the client has opened the contract preview."""
    _require_session(uuid, signing_session)
    service = SubmissionService(db)
    service.record_contract_viewed(uuid)
    return {"ok": True}


@router.post("/submissions/{uuid}/decline")
def decline(
    uuid: str,
    request: Request,
    db: Session = Depends(get_db),
    signing_session: str | None = Cookie(default=None),
):
    _require_session(uuid, signing_session)
    service = SubmissionService(db)
    ip = request.client.host if request.client else "unknown"
    return service.decline(uuid, ip)


@router.post("/submissions/{uuid}/sign")
@limiter.limit("3/minute")
def sign(
    uuid: str,
    body: SignRequest,
    request: Request,
    db: Session = Depends(get_db),
    signing_session: str | None = Cookie(default=None),
):
    """
    Sign the contract. Personal data in request body is NEVER logged or persisted.
    Renders PDF in RAM, encrypts for owner, streams PDF directly to client.
    Rate limited to 3 attempts/minute per IP.
    """
    session_payload = _require_session(uuid, signing_session)
    code_verified_at = datetime.fromisoformat(session_payload["verified_at"])

    contract_viewed_at: datetime | None = None
    if body.contract_viewed_at:
        try:
            contract_viewed_at = datetime.fromisoformat(body.contract_viewed_at)
        except ValueError:
            pass

    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent")

    service = SubmissionService(db)

    # Logging: only UUID and outcome will appear — body is NOT logged
    logger.info("sign attempt submission=%s ip=%s", uuid, ip)

    pdf_bytes = service.sign(
        uuid=uuid,
        payload=body.payload,
        signature_image=body.signature_image,
        signer_full_name=body.signer_full_name,
        confirmed_read=body.confirmed_read,
        confirmed_esign=body.confirmed_esign,
        ip=ip,
        user_agent=user_agent,
        browser_language=body.browser_language,
        timezone=body.timezone,
        screen_resolution=body.screen_resolution,
        code_verified_at=code_verified_at,
        contract_viewed_at=contract_viewed_at,
    )

    logger.info("sign success submission=%s", uuid)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="contract.pdf"'},
    )


@router.post("/download/owner/{uuid}")
def owner_download(
    uuid: str,
    body: OwnerDownloadRequest,
    request: Request,
    k: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Owner downloads their copy of the signed PDF.
    Requires: JWT auth (owner identity), 6-digit download code, AES key from URL (?k=...).
    One-time: blob is wiped and submission marked completed after successful download.
    """
    service = SubmissionService(db)
    pdf_bytes = service.owner_download(
        uuid=uuid,
        code=body.code,
        aes_key_b64=k,
        owner=current_user,
    )

    logger.info("owner download success submission=%s user=%s", uuid, current_user.id)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="contract-signed.pdf"'},
    )
