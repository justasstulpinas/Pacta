from app.services.authorization import is_admin
from app.services.ownership import require_ownership

def require_owner_or_admin(resource_owner_id: int, user) -> None:
    if is_admin(user):
        return
    
    require_ownership(resource_owner_id, user.id)