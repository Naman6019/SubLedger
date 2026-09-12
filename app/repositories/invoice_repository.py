from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from app.repositories.base_repository import BaseRepository


class InvoiceRepository(BaseRepository):
    def create(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        statement = select(Invoice).where(Invoice.id == invoice_id)
        return self.db.scalars(statement).first()

    def list_by_subscription_id(self, subscription_id: int) -> List[Invoice]:
        statement = select(Invoice).where(Invoice.subscription_id == subscription_id)
        return list(self.db.scalars(statement).all())

    def update_payment(self, invoice: Invoice, amount_paid: Decimal, status: str) -> Invoice:
        invoice.amount_paid = amount_paid
        invoice.status = status
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
