from fastapi import Depends
from app.dependencies.auth import get_current_user
from app.services.authorization import require_permission
from app.models.user import User


def permission_required(permission: str):
    def dependency(user: User = Depends(get_current_user)):
        require_permission(user, permission)
        return user

    return dependency
