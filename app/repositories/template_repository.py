from sqlalchemy.orm import Session

from app.models.contract_template import ContractTemplate
from app.models.contract_template_versions import ContractTemplateVersion
from app.models.filled_contract import FilledContract
from app.models.public_link import PublicLink


class TemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, template_id: int) -> ContractTemplate | None:
        return (
            self.db.query(ContractTemplate)
            .filter(ContractTemplate.id == template_id)
            .first()
        )

    def get_active_by_id(self, template_id: int) -> ContractTemplate | None:
        return (
            self.db.query(ContractTemplate)
            .filter(
                ContractTemplate.id == template_id,
                ContractTemplate.status == "active",
                ContractTemplate.is_deleted == False,
            )
            .first()
        )

    def list_by_owner(self, owner_id: int) -> list[ContractTemplate]:
        return (
            self.db.query(ContractTemplate)
            .filter(
                ContractTemplate.owner_id == owner_id,
                ContractTemplate.is_deleted == False,
            )
            .all()
        )

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

    def get_active_template_for_public(self, template_id: int) -> ContractTemplate | None:
        return (
            self.db.query(ContractTemplate)
            .filter(
                ContractTemplate.id == template_id,
                ContractTemplate.status == "active",
                ContractTemplate.is_deleted == False,
            )
            .first()
        )

    def get_valid_link(self, token: str) -> PublicLink | None:
        return (
            self.db.query(PublicLink)
            .filter(
                PublicLink.token == token,
                PublicLink.is_revoked == False,
            )
            .first()
        )

    def get_submission_by_id(self, submission_id: int) -> FilledContract | None:
        return (
            self.db.query(FilledContract)
            .filter(FilledContract.id == submission_id)
            .first()
        )