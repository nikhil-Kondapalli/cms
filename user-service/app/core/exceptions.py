class AppException(Exception):
    status_code = 500
    detail = "Internal Server Error"

    def __init__(self, detail=None):
        if detail:
            self.detail = detail


class NotFoundException(AppException):
    status_code = 404


class ConflictException(AppException):
    status_code = 409


class BadRequestException(AppException):
    status_code = 400


class UserNotFoundException(NotFoundException):
    detail = "User not found"


class EmailAlreadyExistsException(ConflictException):
    detail = "Email already exists"
