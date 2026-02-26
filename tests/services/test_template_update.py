import pytest
from app.services.template_service import TemplateService
from app.schemas.contract_template import ContractTemplateUpdate
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.contract_template import ContractTemplate


def test_owner_can_update(db_session, test_user):
    template = ContractTemplate(
        owner_id=test_user.id,
        name="Old",
        description="Old desc",
        content="Old content",
        status="draft",
        is_deleted=False,
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)

    service = TemplateService(db_session)

    payload = ContractTemplateUpdate(name="New Name")

    updated = service.update_template(template.id, payload, test_user)

    assert updated.name == "New Name"
    assert updated.owner_id == test_user.id


def test_non_owner_cannot_update(db_session, test_user, another_user):
    template = ContractTemplate(
        owner_id=another_user.id,
        name="Old",
        description="Old",
        content="Old",
        status="draft",
        is_deleted=False,
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)

    service = TemplateService(db_session)

    payload = ContractTemplateUpdate(name="New")

    with pytest.raises(ForbiddenError):
        service.update_template(template.id, payload, test_user)


def test_soft_deleted_returns_404(db_session, test_user):
    template = ContractTemplate(
        owner_id=test_user.id,
        name="Old",
        description="Old",
        content="Old",
        status="draft",
        is_deleted=True,
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)

    service = TemplateService(db_session)

    payload = ContractTemplateUpdate(name="New")

    with pytest.raises(NotFoundError):
        service.update_template(template.id, payload, test_user)