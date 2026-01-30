import pytest
from app.services.authorization import require_permission
from app.core.exceptions import ForbiddenError

class FakeUser:
    def __init__(self, permissions):
        self.roles = [
            type(
                "Role",
                (),
                {"permissions": [type("Perm", (), {"code": p})() for p in permissions]},
            )()
        ]

def test_require_permission_forbidden():
    user = FakeUser(permissions=["template:read"])

    with pytest.raises(ForbiddenError):
        require_permission(user, "template:create")
