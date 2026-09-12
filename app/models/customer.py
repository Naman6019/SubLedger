from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    company_name = Column(String(100), nullable=True)
    status = Column(String(20), default="active", nullable=False)  # active, inactive
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="customer", cascade="all, delete-orphan")
    ledger_entries = relationship("LedgerEntry", back_populates="customer", cascade="all, delete-orphan")
