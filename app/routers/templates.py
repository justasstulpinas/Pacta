import io
import mammoth
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.contract_template import (
    ContractTemplateCreate,
    ContractTemplateListItem,
    ContractTemplateOut,
    ContractTemplateUpdate
)
from app.schemas.filled_contract import FilledContractResponse

from app.services.contract_service import ContractService
from app.services.template_service import TemplateService


router = APIRouter(
    prefix="/templates",
    tags=["templates"],
)


@router.post(
    "",
    response_model=ContractTemplateOut,
    status_code=status.HTTP_201_CREATED,
)
def create_template(
    payload: ContractTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.create_template(payload, current_user)


@router.get(
    "",
    response_model=list[ContractTemplateListItem],
)
def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
    name: str | None = None,
):
    service = TemplateService(db)
    return service.list_user_templates(current_user, limit=limit, offset=offset, status=status, name=name)


@router.get(
    "/{template_id}",
    response_model=ContractTemplateOut,
)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.get_template_by_id(template_id, current_user)


@router.get(
    "/{template_id}/submissions",
    response_model=list[FilledContractResponse],
)
def get_submissions(
    template_id: int,
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ContractService(db)
    return service.get_template_submissions(
        template_id=template_id,
        user=current_user,
        limit=limit,
        offset=offset,
        status=status,
    )


@router.post(
    "/{template_id}/duplicate",
    response_model=ContractTemplateOut,
    status_code=status.HTTP_201_CREATED,
)
def duplicate_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.duplicate_template(template_id, current_user)


@router.patch(
    "/{template_id}/activate",
    response_model=ContractTemplateOut,
)
def activate_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.activate_template(template_id, current_user)


@router.patch(
    "/{template_id}/archive",
    response_model=ContractTemplateOut,
)
def archive_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.archive_template(template_id, current_user)


@router.delete(
    "/{template_id}",
    response_model=ContractTemplateOut,
)
def soft_delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.soft_delete_template(template_id, current_user)

@router.put(
    "/{template_id}",
    response_model=ContractTemplateOut,
)
def update_template(
    template_id: int,
    payload: ContractTemplateUpdate,
    db: Session =Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TemplateService(db)
    return service.update_template(template_id, payload, current_user)


@router.post("/upload-docx")
async def upload_docx(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not (file.filename or "").lower().endswith(".docx"):
        from app.core.exceptions import BadRequestError
        raise BadRequestError("Tik .docx formato failai palaikomi")

    data = await file.read()
    return {"html": _docx_to_tiptap_html(data)}


def _docx_to_tiptap_html(data: bytes) -> str:
    import re
    import html as _html
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document(io.BytesIO(data))
    parts: list[str] = []

    _OPEN_TAG = re.compile(r'^<([a-zA-Z]+)(\s[^>]*)?>$')
    _CLOSE_TAG = re.compile(r'^</[a-zA-Z]+>$')
    _STYLE_ATTR = re.compile(r'style=["\']([^"\']*)["\']')
    _CSS_COLOR = re.compile(r'color\s*:\s*([^;]+)')
    _CSS_SIZE = re.compile(r'font-size\s*:\s*([^;]+)')
    _HTML_TAGS = re.compile(r'<[^>]+>')

    def _para_content(para) -> str:
        result = []
        pending: dict = {}  # styles from embedded opening tags

        for run in para.runs:
            text = run.text
            stripped = text.strip()

            # Detect embedded HTML opening tags (e.g. the run IS a <span style="...">)
            if _OPEN_TAG.match(stripped):
                style_m = _STYLE_ATTR.search(stripped)
                if style_m:
                    style_str = style_m.group(1).replace('&quot;', '"')
                    cm = _CSS_COLOR.search(style_str)
                    sm = _CSS_SIZE.search(style_str)
                    if cm:
                        pending['color'] = cm.group(1).strip()
                    if sm:
                        pending['font-size'] = sm.group(1).strip()
                continue

            # Detect embedded HTML closing tags
            if _CLOSE_TAG.match(stripped):
                pending.clear()
                continue

            # Real text — strip any remaining stray HTML tags
            clean = _HTML_TAGS.sub('', text)
            if not clean.strip():
                continue

            t = _html.escape(clean)

            # Apply Word run formatting
            if run.bold:
                t = f"<strong>{t}</strong>"
            if run.italic:
                t = f"<em>{t}</em>"
            if run.underline:
                t = f"<u>{t}</u>"

            # Apply accumulated inline styles from embedded tags
            if pending:
                style_str = '; '.join(f'{k}: {v}' for k, v in pending.items())
                t = f'<span style="{style_str}">{t}</span>'

            result.append(t)

        return ''.join(result)

    for para in doc.paragraphs:
        raw = _HTML_TAGS.sub('', para.text).strip()
        if not raw:
            parts.append("<p></p>")
            continue

        style_name = (para.style.name or "").lower()
        content = _para_content(para) or _html.escape(raw)

        align_style = ""
        try:
            if para.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                align_style = ' style="text-align: center;"'
            elif para.alignment == WD_ALIGN_PARAGRAPH.RIGHT:
                align_style = ' style="text-align: right;"'
            elif para.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY:
                align_style = ' style="text-align: justify;"'
        except Exception:
            pass

        if "heading 1" in style_name or "title" in style_name:
            parts.append(f"<h1{align_style}>{content}</h1>")
        elif "heading 2" in style_name or "subtitle" in style_name:
            parts.append(f"<h2{align_style}>{content}</h2>")
        elif "heading 3" in style_name:
            parts.append(f"<h3{align_style}>{content}</h3>")
        elif "list" in style_name:
            parts.append(f"<li>{content}</li>")
        else:
            parts.append(f"<p{align_style}>{content}</p>")

    return "\n".join(parts)
