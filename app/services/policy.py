from app.core.exceptions import ForbiddenError
import app.services.authorization as authorization


def require_owner_or_admin(resource_owner_id: int, user) -> None:
    if resource_owner_id == user.id:
        return

    if authorization.is_admin(user):
        return

    raise ForbiddenError("Access denied")


def require_owner(resource_owner_id: int, user) -> None:
    if resource_owner_id != user.id:
        raise ForbiddenError("Access denied")


def require_admin(user) -> None:
    if not authorization.is_admin(user):
        raise ForbiddenError("Admin only")