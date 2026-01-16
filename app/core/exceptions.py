class AppError(Exception):
    """Bazinė aplikacijos klaida"""
    pass

class InvalidCredentialsError(AppError):
    """"Neteisingi prisijungimo duomenys"""
    pass

class PermissionDeniedError(AppError):
    """Neturi teisių atlikti veiksmų"""
    pass

class NotFoundError(AppError):
    """Resursas nerastas"""
    pass

# day 5 sukurtas exceptions error failas kuris skirtas identifikuoti errora