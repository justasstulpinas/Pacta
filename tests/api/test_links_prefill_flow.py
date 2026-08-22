from datetime import UTC, datetime

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
from app.models.filled_contract import FilledContract
from app.models.public_link import PublicLink
from app.models.user import User


TEMPLATE_CONTENT = (
    "Agreement between {{owner_company}} and {{client_name}}.\n"
    "Date: {{sys_current_date}}\n"
    "Timestamp: {{sys_current_datetime}}"
)


@pytest.fixture
def links_prefill_ctx():
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

    setup_db = testing_session_local()
    owner = User(email="links-owner@example.com", hashed_password="hashed")
    setup_db.add(owner)
    setup_db.flush()

    template = ContractTemplate(
        owner_id=owner.id,
        name="Public Link Template",
        description="Template with owner/system placeholders",
        content=TEMPLATE_CONTENT,
        status=TemplateStatus.ACTIVE.value,
        is_deleted=False,
    )
    setup_db.add(template)
    setup_db.flush()

    version = ContractTemplateVersion(
        template_id=template.id,
        version_number=1,
        content=TEMPLATE_CONTENT,
    )
    setup_db.add(version)
    setup_db.commit()

    owner_id = owner.id
    template_id = template.id
    setup_db.close()

    def override_get_db():
        request_db = testing_session_local()
        try:
            yield request_db
        finally:
            request_db.close()

    def override_get_current_user():
        request_db = testing_session_local()
        try:
            return request_db.query(User).filter(User.id == owner_id).first()
        finally:
            request_db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    client = TestClient(app)

    try:
        yield client, testing_session_local, template_id
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


def _create_link_with_prefill(client: TestClient, template_id: int) -> dict:
    response = client.post(
        "/links",
        json={
            "template_id": template_id,
            "expires_in_hours": 24,
            "prefill": {"owner_company": "Melno UAB"},
        },
    )
    assert response.status_code == 200
    return response.json()


def test_post_links_succeeds_with_owner_prefill_and_resolves_sys_date(links_prefill_ctx):
    client, testing_session_local, template_id = links_prefill_ctx
    payload = _create_link_with_prefill(client, template_id)

    db = testing_session_local()
    try:
        link = db.query(PublicLink).filter(PublicLink.id == payload["id"]).first()
        assert link is not None
        assert link.resolved_content is not None
        assert "{{owner_company}}" not in link.resolved_content
        assert "{{sys_current_date}}" not in link.resolved_content
        assert "{{sys_current_datetime}}" not in link.resolved_content
        assert "Melno UAB" in link.resolved_content
        assert datetime.now(UTC).date().isoformat() in link.resolved_content
        assert "{{client_name}}" in link.resolved_content
    finally:
        db.close()


def test_post_links_returns_400_for_missing_owner_fields(links_prefill_ctx):
    client, _, template_id = links_prefill_ctx

    response = client.post(
        "/links",
        json={
            "template_id": template_id,
            "expires_in_hours": 24,
            "prefill": {},
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "missing_owner_fields": ["owner_company"],
            "extra_owner_fields": [],
        }
    }


def test_post_links_returns_400_for_extra_owner_fields(links_prefill_ctx):
    client, _, template_id = links_prefill_ctx

    response = client.post(
        "/links",
        json={
            "template_id": template_id,
            "expires_in_hours": 24,
            "prefill": {
                "owner_company": "Melno UAB",
                "unknown_field": "X",
            },
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "missing_owner_fields": [],
            "extra_owner_fields": ["unknown_field"],
        }
    }


def test_get_public_template_returns_only_public_fields(links_prefill_ctx):
    client, _, template_id = links_prefill_ctx
    link_payload = _create_link_with_prefill(client, template_id)

    response = client.get(f"/links/public/{link_payload['token']}")
    assert response.status_code == 200

    body = response.json()
    assert body["fields"] == ["client_name"]
    assert "{{owner_company}}" not in body["content"]
    assert "{{sys_current_date}}" not in body["content"]
    assert "{{sys_current_datetime}}" not in body["content"]
    assert "{{client_name}}" in body["content"]


def test_public_submit_succeeds_with_only_public_fields(links_prefill_ctx):
    client, testing_session_local, template_id = links_prefill_ctx
    link_payload = _create_link_with_prefill(client, template_id)

    response = client.post(
        f"/links/public/{link_payload['token']}/submit",
        json={"client_name": "Alice"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "submitted"
    submission_id = response.json()["id"]

    db = testing_session_local()
    try:
        submission = (
            db.query(FilledContract)
            .filter(FilledContract.id == submission_id)
            .first()
        )
        assert submission is not None
        assert submission.submitted_data == {"client_name": "Alice"}
        assert "Melno UAB" in submission.rendered_content
        assert "Alice" in submission.rendered_content
        assert datetime.now(UTC).date().isoformat() in submission.rendered_content
        assert "{{" not in submission.rendered_content
    finally:
        db.close()
