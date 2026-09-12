class SubLedgerException(Exception):
    """Base exception for all SubLedger domain errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class EntityNotFoundException(SubLedgerException):
    """Raised when a requested resource does not exist."""
    pass


class BusinessRuleViolationException(SubLedgerException):
    """Raised when a business constraint or domain invariant is violated."""
    pass


class ConflictException(SubLedgerException):
    """Raised when an operation conflicts with current state (e.g. duplicate email/subscription)."""
    pass


class InvalidStateTransitionException(SubLedgerException):
    """Raised when an illegal status change is attempted."""
    pass
