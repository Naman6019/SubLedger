from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.ledger import LedgerEntry
from app.repositories.base_repository import BaseRepository


class LedgerRepository(BaseRepository):
    """
    Append-only repository for accounting and auditing ledger events.
    Does NOT provide update or delete methods to preserve immutability.
    """

    def create(self, ledger_entry: LedgerEntry) -> LedgerEntry:
        self.db.add(ledger_entry)
        self.db.commit()
        self.db.refresh(ledger_entry)
        return ledger_entry

    def get_by_id(self, entry_id: int) -> Optional[LedgerEntry]:
        statement = select(LedgerEntry).where(LedgerEntry.id == entry_id)
        return self.db.scalars(statement).first()

    def list_by_customer_id(
        self,
        customer_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[LedgerEntry]:
        statement = (
            select(LedgerEntry)
            .where(LedgerEntry.customer_id == customer_id)
            .order_by(LedgerEntry.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def list_by_reference_id(self, reference_id: str) -> List[LedgerEntry]:
        statement = (
            select(LedgerEntry)
            .where(LedgerEntry.reference_id == reference_id)
            .order_by(LedgerEntry.created_at.asc())
        )
        return list(self.db.scalars(statement).all())
