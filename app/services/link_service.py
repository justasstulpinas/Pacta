import uuid 
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.public_link import PublicLink
from app.models.contract_template import ContractTemplate
from app.models.user import User
from app.core.exceptions import NotFoundError, ForbiddenError
from app.services.authorization import is_admin

class LinkService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_public_link(
            self,
            template_id: int,
            expires_in_hours: int,
            user: User,
    )-> PublicLink:
        
        template = (
            self.db.query(ContractTemplate)
            .filter(
                ContractTemplate.id == template_id,
                ContractTemplate.is_deleted == False,
            )
            .first()
        )

        if not template:
            raise NotFoundError("template not found")
        if template.owner_id != user.id and not is_admin(user):
            raise ForbiddenError('access denied')
        if template.status != "active":
            raise ForbiddenError('only active templates can generate public links')
        
        token = str(uuid.uuid4())

        link = PublicLink(
            template_id= template.id,
            token= token,
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
            )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)

        return link