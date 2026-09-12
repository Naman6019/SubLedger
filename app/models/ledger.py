from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True, index=True)
    entry_type = Column(String(50), nullable=False)  # invoice_created, payment_success, payment_failure
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    reference_id = Column(String(100), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="ledger_entries")
    invoice = relationship("Invoice", back_populates="ledger_entries")
