from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.exceptions import ForbiddenError, NotFoundError
from app.database import Base
from app.models.contract_template import ContractTemplate
from app.models.enums import ContractTemplateStatus
from app.models.filled_contract import FilledContract
from app.models.public_link import PublicLink
from app.models.role import Role  # noqa: F401
from app.models.user import User
from app.services.contract_service import ContractService


def _build_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    test_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)
    return engine, test_session()


def test_owner_can_list_template_submissions_ordered_desc():
    engine, db = _build_session()
    try:
        owner = User(email="owner@example.com", hashed_password="hashed")
        db.add(owner)
        db.flush()

        template = ContractTemplate(
            owner_id=owner.id,
            name="T",
            description=None,
            content="C",
            status=ContractTemplateStatus.ACTIVE.value,
            is_deleted=False,
        )
        db.add(template)
        db.flush()

        link = PublicLink(
            template_id=template.id,
            token="token-1",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            is_revoked=False,
        )
        db.add(link)
        db.flush()

        older = FilledContract(
            template_id=template.id,
            template_version=2,
            link_id=link.id,
            submitted_data={"a": "1"},
            rendered_content="old",
            ip_address="127.0.0.1",
            user_agent="pytest",
            submission_hash="hash-old",
            status="submitted",
            submitted_at=datetime(2026, 1, 1, 10, 0, 0),
        )
        newer = FilledContract(
            template_id=template.id,
            template_version=3,
            link_id=link.id,
            submitted_data={"a": "2"},
            rendered_content="new",
            ip_address="127.0.0.1",
            user_agent="pytest",
            submission_hash="hash-new",
            status="submitted",
            submitted_at=datetime(2026, 1, 1, 11, 0, 0),
        )
        db.add_all([older, newer])
        db.commit()

        service = ContractService(db)
        result = service.get_template_submissions(template.id, owner)

        assert [row.id for row in result] == [newer.id, older.id]
        assert result[0].template_version == 3
        assert result[0].rendered_content == "new"
        assert result[0].status == "submitted"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_non_owner_cannot_list_template_submissions():
    engine, db = _build_session()
    try:
        owner = User(email="owner@example.com", hashed_password="hashed")
        other = User(email="other@example.com", hashed_password="hashed")
        db.add_all([owner, other])
        db.flush()

        template = ContractTemplate(
            owner_id=owner.id,
            name="T",
            description=None,
            content="C",
            status=ContractTemplateStatus.ACTIVE.value,
            is_deleted=False,
        )
        db.add(template)
        db.commit()

        service = ContractService(db)
        with pytest.raises(ForbiddenError):
            service.get_template_submissions(template.id, other)
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_missing_template_returns_not_found():
    engine, db = _build_session()
    try:
        owner = User(email="owner@example.com", hashed_password="hashed")
        db.add(owner)
        db.commit()

        service = ContractService(db)
        with pytest.raises(NotFoundError):
            service.get_template_submissions(template_id=999, user=owner)
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_submissions_support_status_filter_and_pagination():
    engine, db = _build_session()
    try:
        owner = User(email="owner3@example.com", hashed_password="hashed")
        db.add(owner)
        db.flush()

        template = ContractTemplate(
            owner_id=owner.id,
            name="T",
            description=None,
            content="C",
            status=ContractTemplateStatus.ACTIVE.value,
            is_deleted=False,
        )
        db.add(template)
        db.flush()

        link = PublicLink(
            template_id=template.id,
            token="token-2",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            is_revoked=False,
        )
        db.add(link)
        db.flush()

        first_submitted = FilledContract(
            template_id=template.id,
            template_version=1,
            link_id=link.id,
            submitted_data={"n": "1"},
            rendered_content="first",
            ip_address="127.0.0.1",
            user_agent="pytest",
            submission_hash="hash-1",
            status="submitted",
            submitted_at=datetime(2026, 1, 1, 10, 0, 0),
        )
        confirmed = FilledContract(
            template_id=template.id,
            template_version=2,
            link_id=link.id,
            submitted_data={"n": "2"},
            rendered_content="second",
            ip_address="127.0.0.1",
            user_agent="pytest",
            submission_hash="hash-2",
            status="confirmed",
            submitted_at=datetime(2026, 1, 1, 11, 0, 0),
        )
        latest_submitted = FilledContract(
            template_id=template.id,
            template_version=3,
            link_id=link.id,
            submitted_data={"n": "3"},
            rendered_content="third",
            ip_address="127.0.0.1",
            user_agent="pytest",
            submission_hash="hash-3",
            status="submitted",
            submitted_at=datetime(2026, 1, 1, 12, 0, 0),
        )
        db.add_all([first_submitted, confirmed, latest_submitted])
        db.commit()

        service = ContractService(db)
        result = service.get_template_submissions(
            template_id=template.id,
            user=owner,
            limit=1,
            offset=1,
            status="submitted",
        )

        assert len(result) == 1
        assert result[0].id == first_submitted.id
        assert result[0].status == "submitted"
        assert result[0].rendered_content == "first"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
