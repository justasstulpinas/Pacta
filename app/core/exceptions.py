
# exceptionai skirti skirtingoms sitaucijoms

class AppError(Exception):
    pass


class InvalidCredentialsError(AppError):
    pass


class PermissionDeniedError(AppError):
    pass


class NotFoundError(AppError):
    pass


class ForbiddenError(AppError):
    pass

class BadRequestError(AppError):
    def __init__(self, detail: str = "Bad request"):
        self.detail = detail
        super().__init__(detail)

class UnauthorizedError(AppError):
    pass

class RateLimitExceeded(AppError):
    pass

class ValidationError(Exception):
    def __init__(self, detail):
        self.detail = detail
        super().__init__(str(detail))

