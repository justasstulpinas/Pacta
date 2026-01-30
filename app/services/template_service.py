from app.core.exceptions import NotFoundError, ForbiddenError
from app.services.authorization import is_admin
from app.services.ownership import require_ownership
from app.models.template import ContractTemplate
from sqlalchemy.orm import Session

def get_template(
    db: Session,
    template_id: int,
    user,
    ):
    template = db.query(ContractTemplate).filter_by(id=template_id).first()

    if not template:
        raise NotFoundError()
    
    if not is_admin(user):
        require_ownership(template.owner_id, user.id)
    
    return template