from app.core.exceptions import ForbiddenError
from app.models.contract_template import ContractTemplate
from app.models.filled_contract import FilledContract
from app.models.user import User

# policy klase skirtia leidimu ir roliu centralizavimui, maziau klaidu jei kodas pleciasi nes visos policies yra vienoje vietoje
class PolicyService:
    @staticmethod
    def get_user_permissions(user: User) -> set[str]:
        permissions: set[str] = set()
        for role in getattr(user, "roles", []):
            for permission in getattr(role, "permissions", []):
                permissions.add(permission.code)
        return permissions

    @classmethod
    def is_admin(cls, user: User) -> bool:
        return "admin:all" in cls.get_user_permissions(user)

    @classmethod
    def require_permission(cls, user: User, permission: str) -> None:
        if permission not in cls.get_user_permissions(user):
            raise ForbiddenError(f"Missing permission: {permission}")

    @classmethod
    def check_template_access(cls, user: User, template: ContractTemplate) -> None:
        if template.owner_id == user.id:
            return
        if cls.is_admin(user):
            return
        raise ForbiddenError("Access denied")

    @classmethod
    def check_submission_access(cls, user: User, submission: FilledContract) -> None:
        cls.check_template_access(user, submission.template)

    @classmethod
    def require_owner(cls, resource_owner_id: int, user: User) -> None:
        if resource_owner_id != user.id:
            raise ForbiddenError("Access denied")

    @classmethod
    def require_admin(cls, user: User) -> None:
        if not cls.is_admin(user):
            raise ForbiddenError("Admin only")


def require_owner_or_admin(resource_owner_id: int, user: User) -> None:
    if resource_owner_id == user.id:
        return
    from app.services import authorization as authorization_service

    if authorization_service.is_admin(user):
        return
    raise ForbiddenError("Access denied")


def require_owner(resource_owner_id: int, user: User) -> None:
    PolicyService.require_owner(resource_owner_id, user)


def require_admin(user: User) -> None:
    PolicyService.require_admin(user)
