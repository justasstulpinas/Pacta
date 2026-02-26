import uuid 
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.public_link import PublicLink
from app.models.contract_template import ContractTemplate
from app.models.filled_contract import FilledContract
from app.services.placeholder_service import PlaceholderService
from app.models.user import User
from app.core.exceptions import NotFoundError, ForbiddenError
from app.services.authorization import is_admin
from app.services.placeholder_service import PlaceholderService

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
    
    def get_public_template(self, token:str):
        link = (
            self.db.query(PublicLink)
            .filter(
                PublicLink.token == token,
                PublicLink.is_revoked == False,
                )
                .first()
       )
        if not link:
            raise NotFoundError('request not found')
        
        if link.expires_at <= datetime.utcnow():
            raise NotFoundError('request not found')
        template = (
            self.db.query(ContractTemplate)
            .filter(
                ContractTemplate.id == link.template_id,
                ContractTemplate.is_deleted == False,
                ContractTemplate.status == "active",
            )
            .first()
        )
        if not template: raise NotFoundError('request not found')

        return template
    
    def get_public_template(self, token: str):
        link = (
            self.db.query(PublicLink)
            .filter(
                PublicLink.token == token,
                PublicLink.is_revoked == False,
            )
            .first()
        )
        if not link:
            raise NotFoundError("request not found")
        if link.expires_at <= datetime.utcnow():
            raise NotFoundError('request not found')
        
        template = (
            self.db.query(ContractTemplate)
            .filter(
                ContractTemplate.id == link.template_id,
                ContractTemplate.is_deleted == False,
                ContractTemplate.status == "active",
            )
            .first()
        )
        if not template:
            raise NotFoundError("request not found")
        
        fields = PlaceholderService.extract_placeholders(template.content)

        return{
            "name": template.name,
            "description": template.description,
            "content": template.content,
            "fields": fields,
        }
    
    def submit_public_contract(self, token: str, payload: dict):
        link = (
            self.db.query(PublicLink)
            .filter(
                PublicLink.token == token,
                PublicLink.is_revoked == False,
            )
            .first()
        )

        if not link:
            raise NotFoundError("Request not found")

        if link.expires_at <= datetime.utcnow():
            raise NotFoundError("Request not found")

        template = (
            self.db.query(ContractTemplate)
            .filter(
                ContractTemplate.id == link.template_id,
                ContractTemplate.is_deleted == False,
                ContractTemplate.status == "active",
            )
            .first()
        )

        if not template:
            raise NotFoundError("Request not found")

        expected_fields = PlaceholderService.extract_placeholders(template.content)

        PlaceholderService.validate_payload(expected_fields, payload)

        filled = FilledContract(
            template_id=template.id,
            link_id=link.id,
            submitted_data=payload,
        )

        self.db.add(filled)
        self.db.commit()
        self.db.refresh(filled)

        return {"status": "submitted", "id": filled.id}