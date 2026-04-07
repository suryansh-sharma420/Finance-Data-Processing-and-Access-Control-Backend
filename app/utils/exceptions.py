from fastapi import HTTPException, status

class CustomException(HTTPException):
    """Base class for all system-specific exceptions."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class UnauthorizedUser(CustomException):
    """Raised when authentication fails."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

class ForbiddenAction(CustomException):
    """Raised when a user lacks permission for an action."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

class RecordNotFound(CustomException):
    """Raised when a requested financial record does not exist."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial record not found"
        )

class NegativeAmountException(CustomException):
    """Raised when a record amount is non-positive."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Financial record amount must be positive"
        )
