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
