from datetime import UTC, datetime

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.dependencies.auth import get_current_user
from app.main import app
from app.models.contact import Contact
from app.models.user import User


@pytest.fixture
def contacts_api_ctx():
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
    owner = User(email="contacts-owner@example.com", hashed_password="hashed")
    other_user = User(email="contacts-other@example.com", hashed_password="hashed")
    setup_db.add_all([owner, other_user])
    setup_db.commit()
    setup_db.refresh(owner)
    setup_db.refresh(other_user)
    owner_id = owner.id
    other_user_id = other_user.id
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
        yield client, testing_session_local, owner_id, other_user_id
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def contacts_api_no_auth_ctx():
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

    def override_get_db():
        request_db = testing_session_local()
        try:
            yield request_db
        finally:
            request_db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    try:
        yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


def test_list_own_contacts(contacts_api_ctx):
    client, testing_session_local, owner_id, other_user_id = contacts_api_ctx
    db = testing_session_local()
    try:
        first = Contact(
            owner_id=owner_id,
            name="First",
            created_at=datetime(2026, 1, 1, 9, 0, tzinfo=UTC),
            updated_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
        )
        second = Contact(
            owner_id=owner_id,
            name="Second",
            created_at=datetime(2026, 1, 1, 11, 0, tzinfo=UTC),
            updated_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
        )
        other = Contact(
            owner_id=other_user_id,
            name="Other",
            created_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
            updated_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        )
        db.add_all([first, second, other])
        db.commit()
        db.refresh(first)
        db.refresh(second)
    finally:
        db.close()

    response = client.get("/contacts")
    assert response.status_code == 200
    payload = response.json()
    assert [item["id"] for item in payload] == [second.id, first.id]
    assert all(item["owner_id"] == owner_id for item in payload)


def test_create_contact_success(contacts_api_ctx):
    client, testing_session_local, owner_id, _ = contacts_api_ctx
    response = client.post(
        "/contacts",
        json={
            "name": "  John Doe  ",
            "phone": "  +37060000000  ",
            "address": "   ",
            "email": "  john@example.com  ",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["owner_id"] == owner_id
    assert body["name"] == "John Doe"
    assert body["phone"] == "+37060000000"
    assert body["address"] is None
    assert body["email"] == "john@example.com"

    db = testing_session_local()
    try:
        contact = db.query(Contact).filter(Contact.id == body["id"]).first()
        assert contact is not None
        assert contact.owner_id == owner_id
    finally:
        db.close()


def test_create_contact_empty_payload_returns_400(contacts_api_ctx):
    client, _, _, _ = contacts_api_ctx

    response = client.post("/contacts", json={})
    assert response.status_code == 400
    assert response.json() == {"detail": "At least one contact field is required"}


def test_patch_contact_success(contacts_api_ctx):
    client, testing_session_local, owner_id, _ = contacts_api_ctx
    db = testing_session_local()
    try:
        contact = Contact(
            owner_id=owner_id,
            name="Old Name",
            phone="+111",
            address="Old Address",
            email="old@example.com",
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        contact_id = contact.id
    finally:
        db.close()

    response = client.patch(
        f"/contacts/{contact_id}",
        json={
            "name": "  New Name  ",
            "phone": "   ",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "New Name"
    assert body["phone"] is None
    assert body["address"] == "Old Address"
    assert body["email"] == "old@example.com"


def test_patch_contact_empty_payload_returns_400(contacts_api_ctx):
    client, testing_session_local, owner_id, _ = contacts_api_ctx
    db = testing_session_local()
    try:
        contact = Contact(owner_id=owner_id, name="Old Name")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        contact_id = contact.id
    finally:
        db.close()

    response = client.patch(f"/contacts/{contact_id}", json={})
    assert response.status_code == 400
    assert response.json() == {"detail": "At least one field must be provided"}


def test_cannot_update_another_users_contact(contacts_api_ctx):
    client, testing_session_local, _, other_user_id = contacts_api_ctx
    db = testing_session_local()
    try:
        contact = Contact(owner_id=other_user_id, name="Other User Contact")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        contact_id = contact.id
    finally:
        db.close()

    response = client.patch(f"/contacts/{contact_id}", json={"name": "Hack"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Request not found"}


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("get", "/contacts", None),
        ("post", "/contacts", {"name": "John"}),
        ("patch", "/contacts/1", {"name": "John"}),
    ],
)
def test_unauthorized_access_returns_401(
    contacts_api_no_auth_ctx,
    method: str,
    path: str,
    payload: dict | None,
):
    client = contacts_api_no_auth_ctx
    if payload is None:
        response = client.request(method, path)
    else:
        response = client.request(method, path, json=payload)
    assert response.status_code == 401
