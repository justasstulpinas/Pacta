from pathlib import Path

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.dependencies.auth import get_current_user
from app.main import app
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services.profile_service import ProfileService


@pytest.fixture
def profile_api_ctx(tmp_path):
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
    user = User(email="profile-owner@example.com", hashed_password="hashed")
    setup_db.add(user)
    setup_db.commit()
    setup_db.refresh(user)
    user_id = user.id
    setup_db.close()

    avatar_dir = tmp_path / "avatars"
    avatar_dir.mkdir(parents=True, exist_ok=True)
    ProfileService.AVATAR_UPLOAD_DIR = avatar_dir
    ProfileService.AVATAR_PUBLIC_PREFIX = "/uploads/avatars"

    def override_get_db():
        request_db = testing_session_local()
        try:
            yield request_db
        finally:
            request_db.close()

    def override_get_current_user():
        request_db = testing_session_local()
        try:
            return request_db.query(User).filter(User.id == user_id).first()
        finally:
            request_db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    client = TestClient(app)

    try:
        yield client, testing_session_local, user_id, avatar_dir
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def profile_api_no_auth_ctx(tmp_path):
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

    ProfileService.AVATAR_UPLOAD_DIR = tmp_path / "avatars"
    ProfileService.AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ProfileService.AVATAR_PUBLIC_PREFIX = "/uploads/avatars"

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


def test_get_profile_empty_default(profile_api_ctx):
    client, testing_session_local, user_id, _ = profile_api_ctx
    response = client.get("/profile")
    assert response.status_code == 200
    body = response.json()

    assert body["user_id"] == user_id
    assert body["email"] == "profile-owner@example.com"
    assert body["profile_name"] is None
    assert body["company_name"] is None
    assert body["address"] is None
    assert body["phone_number"] is None
    assert body["avatar_url"] is None
    assert body["prefill"] == {
        "name_surname": None,
        "company_name": None,
        "address": None,
        "phone_number": None,
    }

    db = testing_session_local()
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        assert profile is not None
    finally:
        db.close()


def test_update_profile_fields(profile_api_ctx):
    client, _, user_id, _ = profile_api_ctx
    response = client.put(
        "/profile",
        json={
            "profile_name": "  John Smith  ",
            "company_name": "  Pacta  ",
            "address": "   Gedimino pr. 1  ",
            "phone_number": "  +37060000000  ",
        },
    )
    assert response.status_code == 200
    body = response.json()

    assert body["user_id"] == user_id
    assert body["profile_name"] == "John Smith"
    assert body["company_name"] == "Pacta"
    assert body["address"] == "Gedimino pr. 1"
    assert body["phone_number"] == "+37060000000"
    assert body["prefill"] == {
        "name_surname": "John Smith",
        "company_name": "Pacta",
        "address": "Gedimino pr. 1",
        "phone_number": "+37060000000",
    }


def test_upload_avatar_success(profile_api_ctx):
    client, _, _, avatar_dir = profile_api_ctx

    response = client.post(
        "/profile/avatar",
        files={
            "file": ("avatar.png", b"png-bytes", "image/png"),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["avatar_url"] is not None
    assert body["avatar_url"].startswith("/uploads/avatars/")

    filename = body["avatar_url"].split("/")[-1]
    assert (avatar_dir / filename).exists()


def test_upload_avatar_invalid_mime(profile_api_ctx):
    client, _, _, _ = profile_api_ctx
    response = client.post(
        "/profile/avatar",
        files={
            "file": ("avatar.txt", b"hello", "text/plain"),
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid image type"}


def test_upload_avatar_too_large(profile_api_ctx):
    client, _, _, _ = profile_api_ctx
    response = client.post(
        "/profile/avatar",
        files={
            "file": ("avatar.png", b"a" * (5 * 1024 * 1024 + 1), "image/png"),
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Image is too large"}


def test_delete_avatar(profile_api_ctx):
    client, _, _, avatar_dir = profile_api_ctx
    upload = client.post(
        "/profile/avatar",
        files={"file": ("avatar.png", b"png-bytes", "image/png")},
    )
    assert upload.status_code == 200
    avatar_url = upload.json()["avatar_url"]
    filename = avatar_url.split("/")[-1]
    assert (avatar_dir / filename).exists()

    response = client.delete("/profile/avatar")
    assert response.status_code == 200
    assert response.json() == {"avatar_url": None}
    assert not (avatar_dir / filename).exists()


def test_delete_profile_account(profile_api_ctx):
    client, testing_session_local, user_id, _ = profile_api_ctx
    response = client.delete("/profile")
    assert response.status_code == 204
    assert response.content == b""

    db = testing_session_local()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        assert user is None
        assert profile is None
    finally:
        db.close()


@pytest.mark.parametrize(
    ("method", "path", "kwargs"),
    [
        ("get", "/profile", {}),
        ("put", "/profile", {"json": {"profile_name": "John"}}),
        ("delete", "/profile", {}),
        (
            "post",
            "/profile/avatar",
            {"files": {"file": ("avatar.png", b"png-bytes", "image/png")}},
        ),
        ("delete", "/profile/avatar", {}),
    ],
)
def test_unauthorized_access(profile_api_no_auth_ctx, method, path, kwargs):
    client = profile_api_no_auth_ctx
    response = client.request(method, path, **kwargs)
    assert response.status_code == 401
