from app.core.exceptions import ForbiddenError
from app.services.authorization import is_admin


def assert_owner_or_admin(owner_id: int, user) -> None:
    if owner_id != user.id and not is_admin(user):
        raise ForbiddenError("Access denied")
    
def require_ownership(resource_owner_id: int, user_id: int) -> None:
    if resource_owner_id != user_id:
        raise ForbiddenError("Access denied")