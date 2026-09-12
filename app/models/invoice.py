from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_due = Column(Numeric(10, 2), nullable=False)
    amount_paid = Column(Numeric(10, 2), default=0.00, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    status = Column(String(20), default="issued", nullable=False)  # draft, issued, partially_paid, paid, overdue, void
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    subscription = relationship("Subscription", back_populates="invoices")
    customer = relationship("Customer")
    payment_attempts = relationship("PaymentAttempt", back_populates="invoice", cascade="all, delete-orphan")
    ledger_entries = relationship("LedgerEntry", back_populates="invoice", cascade="all, delete-orphan")
