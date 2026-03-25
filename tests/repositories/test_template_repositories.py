import pytest

from app.models.contract_template import ContractTemplate
from app.models.contract_template_versions import ContractTemplateVersion
from app.models.filled_contract import FilledContract
from app.repositories.template_repository import TemplateRepository


def test_get_active_by_id(db, user):
    repo = TemplateRepository(db)

    template = ContractTemplate(
        owner_id=user.id,
        name="Test",
        content="content",
        status="active",
        is_deleted=False,
    )
    db.add(template)
    db.commit()

    result = repo.get_active_by_id(template.id)

    assert result is not None
    assert result.id == template.id


def test_get_active_by_id_excludes_deleted(db, user):
    repo = TemplateRepository(db)

    template = ContractTemplate(
        owner_id=user.id,
        name="Test",
        content="content",
        status="active",
        is_deleted=True,
    )
    db.add(template)
    db.commit()

    result = repo.get_active_by_id(template.id)

    assert result is None


def test_get_latest_version(db, user):
    repo = TemplateRepository(db)

    template = ContractTemplate(
        owner_id=user.id,
        name="Test",
        content="v1",
        status="draft",
    )
    db.add(template)
    db.flush()

    v1 = ContractTemplateVersion(
        template_id=template.id,
        version_number=1,
        content="v1",
    )
    v2 = ContractTemplateVersion(
        template_id=template.id,
        version_number=2,
        content="v2",
    )

    db.add_all([v1, v2])
    db.commit()

    latest = repo.get_latest_version(template.id)

    assert latest.version_number == 2


def test_get_submission_by_id(db):
    repo = TemplateRepository(db)

    submission = FilledContract(
        template_id=1,
        link_id=1,
        submitted_data={"a": "b"},
        rendered_content="x",
        ip_address="127.0.0.1",
        submission_hash="hash",
        status="submitted",
    )

    db.add(submission)
    db.commit()

    result = repo.get_submission_by_id(submission.id)

    assert result is not None