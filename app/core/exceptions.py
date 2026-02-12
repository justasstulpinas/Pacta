class AppError(Exception):
    """Bazinė aplikacijos klaida"""
    pass


class InvalidCredentialsError(AppError):
    """Neteisingi prisijungimo duomenys"""
    pass


class PermissionDeniedError(AppError):
    """Neturi teisių atlikti veiksmų"""
    pass


class NotFoundError(AppError):
    """Resursas nerastas"""
    pass


class ForbiddenError(AppError):
    """Prieiga draudžiama"""
    pass
