from sqlalchemy.orm import Session

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
