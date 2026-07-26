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
    import html as _html
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn

    doc = Document(io.BytesIO(data))
    parts: list[str] = []

    def _run_html(run) -> str:
        text = _html.escape(run.text)
        if not text:
            return ""

        styles: list[str] = []

        # Font color
        try:
            rgb = run.font.color.rgb
            if rgb:
                styles.append(f"color: #{rgb};")
        except Exception:
            pass

        # Font size
        try:
            if run.font.size:
                pt = run.font.size.pt
                styles.append(f"font-size: {pt}pt;")
        except Exception:
            pass

        # Font family
        try:
            name = run.font.name or (
                run._element.find(qn("w:rFonts")) is not None
                and run._element.find(qn("w:rFonts")).get(qn("w:ascii"))
            )
            if name and isinstance(name, str):
                styles.append(f"font-family: '{name}', serif;")
        except Exception:
            pass

        if styles:
            text = f'<span style="{" ".join(styles)}">{text}</span>'
        if run.bold:
            text = f"<strong>{text}</strong>"
        if run.italic:
            text = f"<em>{text}</em>"
        if run.underline:
            text = f"<u>{text}</u>"

        return text

    for para in doc.paragraphs:
        if not para.text.strip():
            parts.append("<p></p>")
            continue

        style_name = (para.style.name or "").lower()
        content = "".join(_run_html(r) for r in para.runs)

        # Alignment
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
