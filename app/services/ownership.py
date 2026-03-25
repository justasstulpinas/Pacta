from app.core.exceptions import ForbiddenError
from app.services.authorization import is_admin


def assert_owner_or_admin(owner_id: int, user) -> None:
    if owner_id != user.id and not is_admin(user):
        raise ForbiddenError("Access denied")