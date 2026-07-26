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

    style_map = """
        p[style-name='Heading 1'] => h1:fresh
        p[style-name='Heading 2'] => h2:fresh
        p[style-name='Heading 3'] => h3:fresh
        p[style-name='Heading 4'] => h4:fresh
        p[style-name='Title'] => h1:fresh
        p[style-name='Subtitle'] => h2:fresh
        r[style-name='Strong'] => strong
        r[style-name='Emphasis'] => em
        p[style-name='List Paragraph'] => li:fresh
    """

    result = mammoth.convert_to_html(
        io.BytesIO(data),
        style_map=style_map,
    )

    return {"html": _clean_docx_html(result.value)}


def _clean_docx_html(html: str) -> str:
    import re
    from bs4 import BeautifulSoup, NavigableString, Tag

    # Fix double-quoted CSS values (e.g. font-family: "Times New Roman")
    # before parsing — the parser itself breaks on unescaped quotes inside attributes.
    # Replace any CSS value wrapped in double quotes with single quotes.
    html = re.sub(r'([\w-]+\s*:\s*)"([^"]*)"', r"\1'\2'", html)

    soup = BeautifulSoup(html, "html.parser")

    BLOCK = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
             "ul", "ol", "li", "table", "tr", "td", "th", "blockquote"}

    # Wrap orphan top-level inline elements in <p> tags
    children = list(soup.children)
    has_orphans = any(
        (isinstance(c, NavigableString) and c.strip()) or
        (isinstance(c, Tag) and c.name not in BLOCK)
        for c in children
    )

    if not has_orphans:
        return str(soup)

    new_soup = BeautifulSoup("", "html.parser")
    bucket: list = []

    def flush():
        if not bucket:
            return
        p = Tag(name="p")
        for el in bucket:
            p.append(el)
        new_soup.append(p)
        bucket.clear()

    for child in list(soup.children):
        child.extract()
        if isinstance(child, Tag) and child.name in BLOCK:
            flush()
            new_soup.append(child)
        elif isinstance(child, NavigableString):
            if "\n" in str(child):
                # Blank line between inline elements = paragraph boundary
                flush()
            # skip the whitespace node itself
        else:
            bucket.append(child)

    flush()
    return str(new_soup)
