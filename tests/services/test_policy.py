import pytest
from app.services.policy import require_owner_or_admin
from app.core.exceptions import ForbiddenError


class DummyUser:
    def __init__(self, id, is_admin=False):
        self.id = id
        self._admin = is_admin

    def is_admin(self):
        return self._admin


def test_owner_allowed():
    user = DummyUser(id=1)
    require_owner_or_admin(1, user)


def test_admin_allowed(monkeypatch):
    user = DummyUser(id=2)

    monkeypatch.setattr("app.services.authorization.is_admin", lambda u: True)

    require_owner_or_admin(1, user)


def test_forbidden():
    user = DummyUser(id=2)

    with pytest.raises(ForbiddenError):
        require_owner_or_admin(1, user)