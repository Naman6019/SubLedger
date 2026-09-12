from decimal import Decimal
from typing import List, Optional
from app.core.exceptions import BusinessRuleViolationException
from app.models.ledger import LedgerEntry
from app.repositories.ledger_repository import LedgerRepository


class LedgerService:
    VALID_ENTRY_TYPES = {"invoice_created", "payment_success", "payment_failure"}

    def __init__(self, ledger_repo: LedgerRepository):
        self.ledger_repo = ledger_repo

    def record_entry(
        self,
        customer_id: int,
        invoice_id: Optional[int],
        entry_type: str,
        amount: Decimal,
        currency: str,
        reference_id: str,
        description: Optional[str] = None,
    ) -> LedgerEntry:
        if entry_type not in self.VALID_ENTRY_TYPES:
            raise BusinessRuleViolationException(
                f"Invalid ledger entry type '{entry_type}'. Must be one of {self.VALID_ENTRY_TYPES}."
            )

        entry = LedgerEntry(
            customer_id=customer_id,
            invoice_id=invoice_id,
            entry_type=entry_type,
            amount=amount,
            currency=currency.upper(),
            reference_id=reference_id,
            description=description,
        )
        return self.ledger_repo.create(entry)

    def get_customer_ledger(
        self,
        customer_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[LedgerEntry]:
        return self.ledger_repo.list_by_customer_id(customer_id, skip=skip, limit=limit)

    def get_by_reference_id(self, reference_id: str) -> List[LedgerEntry]:
        return self.ledger_repo.list_by_reference_id(reference_id)
