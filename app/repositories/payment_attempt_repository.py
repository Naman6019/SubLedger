from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.payment import PaymentAttempt
from app.repositories.base_repository import BaseRepository


class PaymentAttemptRepository(BaseRepository):
    def create(self, payment_attempt: PaymentAttempt) -> PaymentAttempt:
        self.db.add(payment_attempt)
        self.db.commit()
        self.db.refresh(payment_attempt)
        return payment_attempt

    def get_by_id(self, attempt_id: int) -> Optional[PaymentAttempt]:
        statement = select(PaymentAttempt).where(PaymentAttempt.id == attempt_id)
        return self.db.scalars(statement).first()

    def list_by_invoice_id(self, invoice_id: int) -> List[PaymentAttempt]:
        statement = select(PaymentAttempt).where(PaymentAttempt.invoice_id == invoice_id)
        return list(self.db.scalars(statement).all())
