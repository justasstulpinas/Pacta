from fastapi import Depends
from app.dependencies.auth import get_current_user
from app.services.policy import PolicyService
from app.models.user import User

# authorizacija tikrian ar useris turi teises atlikti veiksmus
def permission_required(permission: str):
    def dependency(user: User = Depends(get_current_user)):
        PolicyService.require_permission(user, permission)
        return user

    return dependency
