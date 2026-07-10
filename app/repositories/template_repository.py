from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.models.contract_template import ContractTemplate
from app.models.contract_template_versions import ContractTemplateVersion
from app.models.filled_contract import FilledContract
from app.models.public_link import PublicLink
from app.models.enums import TemplateStatus, SubmissionStatus


# sablonu crud centralizavias
class TemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, template_id: int) -> ContractTemplate | None:
        return (
            self.db.query(ContractTemplate)
            .options(joinedload(ContractTemplate.owner))
            .filter(
                ContractTemplate.id == template_id,
                ContractTemplate.is_deleted == False,
            )
            .first()
        )

    def get_active_by_id(self, template_id: int) -> ContractTemplate | None:
        template = self.get_by_id(template_id)
        if not template:
            return None
        if template.status != TemplateStatus.ACTIVE.value:
            return None
        return template

    def list_by_owner(
        self,
        owner_id: int,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        name: str | None = None,
    ) -> list[ContractTemplate]:
        q = self.db.query(ContractTemplate).filter(
            ContractTemplate.owner_id == owner_id,
            ContractTemplate.is_deleted == False,
        )
        if status:
            q = q.filter(ContractTemplate.status == status)
        if name:
            q = q.filter(ContractTemplate.name.ilike(f"%{name}%"))
        return q.offset(offset).limit(limit).all()

    def create_template(
        self,
        *,
        owner_id: int,
        name: str,
        description: str | None,
        content: str,
        status: TemplateStatus,
    ) -> ContractTemplate:
        template = ContractTemplate(
            owner_id=owner_id,
            name=name,
            description=description,
            content=content,
            status=status.value,
        )
        self.db.add(template)
        self.db.flush()
        return template

    def create_version(
        self,
        *,
        template_id: int,
        version_number: int,
        content: str,
    ) -> ContractTemplateVersion:
        version = ContractTemplateVersion(
            template_id=template_id,
            version_number=version_number,
            content=content,
        )
        self.db.add(version)
        return version

    def save_template(self, template: ContractTemplate) -> ContractTemplate:
        self.db.commit()
        self.db.refresh(template)
        return template

    def get_latest_version(self, template_id: int) -> ContractTemplateVersion | None:
        return (
            self.db.query(ContractTemplateVersion)
            .filter(ContractTemplateVersion.template_id == template_id)
            .order_by(ContractTemplateVersion.version_number.desc())
            .first()
        )

    def get_submissions(
        self,
        template_id: int,
        status: str | None,
        limit: int,
        offset: int,
    ) -> list[FilledContract]:

        query = self.db.query(FilledContract).filter(
            FilledContract.template_id == template_id
        )

        if status:
            query = query.filter(FilledContract.status == status)

        return (
            query.order_by(FilledContract.submitted_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def list_links_for_template(self, template_id: int) -> list[PublicLink]:
        return (
            self.db.query(PublicLink)
            .filter(PublicLink.template_id == template_id)
            .order_by(PublicLink.created_at.desc())
            .all()
        )

    def get_public_link_by_token(self, token: str) -> PublicLink | None:
        return (
            self.db.query(PublicLink)
            .filter(
                PublicLink.token == token,
                PublicLink.is_revoked == False,
            )
            .first()
        )

    def get_valid_link(self, token: str) -> PublicLink | None:
        return self.get_public_link_by_token(token)

    def list_all_submissions_for_user(self, owner_id: int) -> list[FilledContract]:
        from app.models.contract_template import ContractTemplate
        return (
            self.db.query(FilledContract)
            .join(ContractTemplate, FilledContract.template_id == ContractTemplate.id)
            .filter(ContractTemplate.owner_id == owner_id)
            .order_by(FilledContract.submitted_at.desc())
            .all()
        )

    def get_submission_by_id(self, submission_id: int) -> FilledContract | None:
        return (
            self.db.query(FilledContract)
            .filter(FilledContract.id == submission_id)
            .first()
        )

    def save_submission(self, submission: FilledContract) -> FilledContract:
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def create_public_link(
        self,
        *,
        template_id: int,
        token: str,
        expires_at: datetime,
        resolved_content: str | None = None,
    ) -> PublicLink:
        link = PublicLink(
            template_id=template_id,
            token=token,
            expires_at=expires_at,
            resolved_content=resolved_content,
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link
    
    def revoke_public_link(self, link_id: int) -> PublicLink | None:
        link = (
            self.db.query(PublicLink)
            .filter(PublicLink.id == link_id)
            .first() 
        )
        if not link:
            return None
        link.is_revoked = True
        self.db.commit()
        self.db.refresh(link)
        return link
    
    

    def create_submission(
        self,
        *,
        template_id: int,
        template_version: int,
        template_version_id: int,
        link_id: int,
        submitted_data: dict[str, str],
        rendered_content: str,
        ip_address: str,
        user_agent: str | None,
        submission_hash: str,
        signature_image: str | None,
        submitter_email: str,
        status: SubmissionStatus,
    ) -> FilledContract:
        submission = FilledContract(
            template_id=template_id,
            template_version=template_version,
            template_version_id=template_version_id,
            link_id=link_id,
            submitted_data=submitted_data,
            rendered_content=rendered_content,
            ip_address=ip_address,
            user_agent=user_agent,
            submission_hash=submission_hash,
            signature_image= signature_image,
            submitter_email=submitter_email,
            status=status.value, 
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission
