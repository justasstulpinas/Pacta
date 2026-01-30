from app.core.exceptions import ForbiddenError

def require_ownership(resource_owner_id: int, user_id: int) -> None:
    if resource_owner_id != user_id:
        raise ForbiddenError()