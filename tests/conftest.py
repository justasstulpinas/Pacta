import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine)

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def db_session(db):
    return db


@pytest.fixture
def user(db):
    user = User(email="test@test.com", hashed_password="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user(db):
    user = User(email="test@test.com", hashed_password="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def another_user(db):
    user = User(email="other@test.com", hashed_password="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user