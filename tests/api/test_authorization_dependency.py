# tests/api/test_authorization_dependency.py

from fastapi import APIRouter, Depends
from app.dependencies.authorization import permission_required
from app.dependencies.auth import get_current_user
from app.core.exceptions import ForbiddenError

# ---------- FAKE ROUTER ----------
router = APIRouter()

@router.get(
    "/secure-test",
    dependencies=[Depends(permission_required("template:create"))],
)
def secure_test():
    return {"ok": True}


# ---------- FAKE USER ----------
class FakeUser:
    def __init__(self, permissions):
        self.roles = [
            type(
                "Role",
                (),
                {"permissions": [type("Perm", (), {"code": p})() for p in permissions]},
            )()
        ]


# ---------- OVERRIDES ----------
def override_user_without_permission():
    return FakeUser(permissions=["template:read"])


def override_user_with_permission():
    return FakeUser(permissions=["template:create"])


# ---------- TESTS ----------
def test_permission_dependency_forbidden(client):
    client.app.dependency_overrides[get_current_user] = (
        override_user_without_permission
    )

    response = client.get("/secure-test")
    assert response.status_code == 403


def test_permission_dependency_ok(client):
    client.app.dependency_overrides[get_current_user] = override_user_with_permission

    response = client.get("/secure-test")
    assert response.status_code == 200
