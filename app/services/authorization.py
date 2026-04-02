from app.models.user import User
from app.services.policy import PolicyService

# authorizacijos business kllase atsakinga uz vartotojo leidimus

class AuthorizationService:
    @staticmethod
    def get_user_permissions(user: User) -> set[str]:
        return PolicyService.get_user_permissions(user)

    @staticmethod
    def is_admin(user: User) -> bool:
        return PolicyService.is_admin(user)

    @staticmethod
    def require_permission(user: User, permission: str) -> None:
        PolicyService.require_permission(user, permission)


def get_user_permissions(user: User) -> set[str]:
    return AuthorizationService.get_user_permissions(user)


def is_admin(user: User) -> bool:
    return AuthorizationService.is_admin(user)


def require_permission(user: User, permission: str) -> None:
    AuthorizationService.require_permission(user, permission)
