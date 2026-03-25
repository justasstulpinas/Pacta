from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.role import Role  # noqa: F401
from app.models.user import User
from app.models.contract_template import ContractTemplate
from app.models.contract_template_versions import ContractTemplateVersion
from app.models.public_link import PublicLink
from app.models.filled_contract import FilledContract
from app.models.enums import ContractTemplateStatus
from app.services.link_service import LinkService


def test_submission_uses_latest_template_version_content():
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

    db = test_session()
    try:
        user = User(
            email="owner@example.com",
            hashed_password="hashed",
        )
        db.add(user)
        db.flush()

        template = ContractTemplate(
            owner_id=user.id,
            name="Versioned Contract",
            description="test",
            content="STALE {{unused_field}}",
            status=ContractTemplateStatus.ACTIVE.value,
            is_deleted=False,
        )
        db.add(template)
        db.flush()

        version_1 = ContractTemplateVersion(
            template_id=template.id,
            version_number=1,
            content="Contract v1 for {{client_name}}",
        )
        version_2 = ContractTemplateVersion(
            template_id=template.id,
            version_number=2,
            content="Contract v2 for {{client_name}}",
        )
        db.add_all([version_1, version_2])
        db.flush()

        link = PublicLink(
            template_id=template.id,
            token="test-token-1",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            is_revoked=False,
        )
        db.add(link)
        db.commit()

        service = LinkService(db)
        result = service.submit_public_contract(
            token="test-token-1",
            payload={"client_name": "Alice"},
            ip="127.0.0.1",
            user_agent="pytest",
        )

        saved = (
            db.query(FilledContract)
            .filter(FilledContract.id == result["id"])
            .first()
        )

        assert result["status"] == "submitted"
        assert saved is not None
        assert saved.template_version == 2
        assert saved.template_version_id == version_2.id
        assert saved.rendered_content == "Contract v2 for Alice"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_submission_keeps_version_locked_content_across_updates():
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

    db = test_session()
    try:
        user = User(
            email="owner2@example.com",
            hashed_password="hashed",
        )
        db.add(user)
        db.flush()

        template = ContractTemplate(
            owner_id=user.id,
            name="Immutable Contract",
            description="test",
            content="Contract v1 for {{client_name}}",
            status=ContractTemplateStatus.ACTIVE.value,
            is_deleted=False,
        )
        db.add(template)
        db.flush()

        version_1 = ContractTemplateVersion(
            template_id=template.id,
            version_number=1,
            content="Contract v1 for {{client_name}}",
        )
        version_2 = ContractTemplateVersion(
            template_id=template.id,
            version_number=2,
            content="old content for {{client_name}}",
        )
        db.add_all([version_1, version_2])
        db.flush()

        link = PublicLink(
            template_id=template.id,
            token="lock-test-token",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            is_revoked=False,
        )
        db.add(link)
        db.commit()

        service = LinkService(db)
        first = service.submit_public_contract(
            token="lock-test-token",
            payload={"client_name": "Alice"},
            ip="127.0.0.1",
            user_agent="pytest",
        )
        assert first["status"] == "submitted"

        version_3 = ContractTemplateVersion(
            template_id=template.id,
            version_number=3,
            content="new content for {{client_name}}",
        )
        db.add(version_3)
        db.commit()

        second = service.submit_public_contract(
            token="lock-test-token",
            payload={"client_name": "Bob"},
            ip="127.0.0.1",
            user_agent="pytest",
        )
        assert second["status"] == "submitted"

        rows = db.execute(
            text(
                "SELECT template_version, rendered_content "
                "FROM filled_contracts ORDER BY id"
            )
        ).fetchall()

        assert rows == [
            (2, "old content for Alice"),
            (3, "new content for Bob"),
        ]
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
