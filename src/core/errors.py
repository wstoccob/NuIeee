from fastapi import HTTPException, status


def not_found(resource: str) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"{resource} not found")


def conflict(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_409_CONFLICT, detail)


def forbidden(detail: str = "Insufficient permissions") -> HTTPException:
    return HTTPException(status.HTTP_403_FORBIDDEN, detail)


def unauthorized(detail: str = "Invalid credentials") -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED, detail, headers={"WWW-Authenticate": "Bearer"}
    )


class DomainError(Exception):
    """Raised by services for expected business-rule failures.

    Messages are shown to end users as-is, so write them for a participant, not a
    developer. main.py converts these into JSON responses.
    """

    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class NotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(DomainError):
    status_code = status.HTTP_409_CONFLICT


class InvalidError(DomainError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
