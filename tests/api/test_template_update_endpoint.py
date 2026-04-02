from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.dependencies.auth import get_current_user
from app.main import app
from app.models.contract_template import ContractTemplate
from app.models.contract_template_versions import ContractTemplateVersion
from app.models.enums import TemplateStatus
from app.models.user import User


@pytest.fixture
def template_update_ctx():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)
    db = testing_session_local()

    owner = User(email="template-owner@example.com", hashed_password="hashed")
    db.add(owner)
    db.commit()
    db.refresh(owner)

    def override_get_db():
        request_db = testing_session_local()
        try:
            yield request_db
        finally:
            request_db.close()

    def override_get_current_user():
        return owner

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    client = TestClient(app)

    try:
        yield client, db, owner
    finally:
        app.dependency_overrides.clear()
        db.close()
        Base.metadata.drop_all(bind=engine)


def _create_template(
    db,
    owner_id: int,
    *,
    status: TemplateStatus,
    content: str = "Original content",
) -> ContractTemplate:
    template = ContractTemplate(
        owner_id=owner_id,
        name="Template Name",
        description="Template Description",
        content=content,
        status=status.value,
        is_deleted=False,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def _create_version(
    db,
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
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def test_update_draft_template_returns_200(template_update_ctx):
    client, db, owner = template_update_ctx
    template = _create_template(db, owner.id, status=TemplateStatus.DRAFT)

    response = client.put(
        f"/templates/{template.id}",
        json={"name": "Updated Draft Name"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Draft Name"


def test_update_active_template_returns_200_and_keeps_active_status(template_update_ctx):
    client, db, owner = template_update_ctx
    template = _create_template(db, owner.id, status=TemplateStatus.ACTIVE)

    response = client.put(
        f"/templates/{template.id}",
        json={"description": "Updated active description"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == TemplateStatus.ACTIVE.value

    db.refresh(template)
    assert template.status == TemplateStatus.ACTIVE.value


def test_update_archived_template_returns_403(template_update_ctx):
    client, db, owner = template_update_ctx
    template = _create_template(db, owner.id, status=TemplateStatus.ARCHIVED)

    response = client.put(
        f"/templates/{template.id}",
        json={"name": "Should fail"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


def test_active_content_change_increments_version_number(template_update_ctx):
    client, db, owner = template_update_ctx
    template = _create_template(
        db,
        owner.id,
        status=TemplateStatus.ACTIVE,
        content="Version one content",
    )
    _create_version(
        db,
        template_id=template.id,
        version_number=1,
        content="Version one content",
    )

    response = client.put(
        f"/templates/{template.id}",
        json={"content": "Version two content"},
    )

    assert response.status_code == 200

    versions = (
        db.query(ContractTemplateVersion)
        .filter(ContractTemplateVersion.template_id == template.id)
        .order_by(ContractTemplateVersion.version_number.asc())
        .all()
    )
    assert len(versions) == 2
    assert versions[-1].version_number == 2
    assert versions[-1].content == "Version two content"


def test_active_name_or_description_update_does_not_increment_version(template_update_ctx):
    client, db, owner = template_update_ctx
    template = _create_template(
        db,
        owner.id,
        status=TemplateStatus.ACTIVE,
        content="Stable content",
    )
    _create_version(
        db,
        template_id=template.id,
        version_number=1,
        content="Stable content",
    )

    response = client.put(
        f"/templates/{template.id}",
        json={
            "name": "Renamed active template",
            "description": "New active description",
        },
    )

    assert response.status_code == 200

    versions = (
        db.query(ContractTemplateVersion)
        .filter(ContractTemplateVersion.template_id == template.id)
        .all()
    )
    assert len(versions) == 1
    assert versions[0].version_number == 1
