from app.services.authorization import is_admin
from app.core.exceptions import ForbiddenError
from app.models.user import User

def require_owner_or_admin(resource_owner_id: int, user: User) -> None:
    if resource_owner_id == user.id:
        return

    if is_admin(user):
        return

    raise ForbiddenError("Access denied")

def require_admin(user: User) -> None:
    if not is_admin(user):
        raise ForbiddenError("Admin privileges required")
    
def require_user(user: User) -> None:
    if user is None:
        raise ForbiddenError("Access denied")