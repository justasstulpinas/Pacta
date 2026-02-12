from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.contract_template import ContractTemplate
from app.models.enums import ContractTemplateStatus


def create_template(
    *,
    db: Session,
    owner_id: int,
    name: str,
    description: str | None,
    content: str,
) -> ContractTemplate:
    template = ContractTemplate(
        owner_id=owner_id,
        name=name.strip(),
        description=description.strip() if description else None,
        content=content,
        status=ContractTemplateStatus.DRAFT,
    )

    db.add(template)
    db.commit()
    db.refresh(template)
    return template

def list_templates_for_owner(
        *,
        db: Session,
        owner_id: int,
        limit: int,
        offset: int,
) -> list[ContractTemplate]:
    stmt = (
        select(ContractTemplate)
        .where(
            ContractTemplate.owner_id == owner_id,
            ContractTemplate.is_deleted.is_(False),
        )
        .order_by(ContractTemplate.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.execute(stmt).scalars().all())

def create_template(db, owner_id: int, name: str, description: str | None, content: str):
    template = ContractTemplate(
        owner_id = owner_id,
        name=name,
        description=description,
        content=content,
        status= ContractTemplateStatus.DRAFT.value,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

def _assert_owner(template: ContractTemplate, user_id: int):
    if template.owner_id != user_id:
        raise HTTPException(status_code=403, detail="forbidden")
    
def activate_template(db, template: ContractTemplate, user_id: int):
    _assert_owner(template, user_id)
    if template.status != "draft":
        raise HTTPException(status_code=409, detail= "Invalid transition")
    template.status = "active"
    db.commit()
    db.refresh(template)
    return template

def archive_template(db, template: ContractTemplate, user_id: int):
    _assert_owner(template, user_id)
    if template.status != "active":
        raise HTTPException(status_code=409, detail= "Invalid transition")
    template.status = "archived"
    db.commit()
    db.refresh(template)
    return template

def soft_delete_template(db, template: ContractTemplate, user_id: int):
    _assert_owner(template, user_id)
    template.is_deleted = True
    db.commit()
    db.refresh(template)
    return template

def create_template(db, owner_id: int, name: str, description: str | None, content: str):
    template = ContractTemplate(
        owner_id=owner_id,
        name=name,
        description=description,
        content=content,
        status= ContractTemplateStatus.DRAFT.value,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

def list_user_templates(db: Session, owner_id: int):
    return (
        db.query(ContractTemplate)
        .filter(
            ContractTemplate.owner_id == owner_id,
            ContractTemplate.is_deleted == False,
        )
        .order_by(ContractTemplate.created_at.desc())
        .all()
    )