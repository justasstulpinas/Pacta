from app.core.exceptions import ForbiddenError


def get_user_permissions(user) -> set[str]:
    permissions = set()

    for role in getattr(user, "roles", []):
        for perm in getattr(role, "permissions", []):
            permissions.add(perm.code)

    return permissions


def require_permission(user, permission: str) -> None:
    if permission not in get_user_permissions(user):
        raise ForbiddenError()

def is_admin(user) -> bool:
    return "admin:all" in get_user_permissions(user)
