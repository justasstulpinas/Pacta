import pytest
from app.core.exceptions import ForbiddenError
from app.services.policy import require_owner


class DummyUser:
    def __init__(self, id):
        self.id = id


def test_require_owner_forbidden():
    user = DummyUser(id=2)

    with pytest.raises(ForbiddenError):
        require_owner(resource_owner_id=1, user=user)


def test_require_owner_ok():
    user = DummyUser(id=1)

    require_owner(resource_owner_id=1, user=user)