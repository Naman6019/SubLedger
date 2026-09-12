from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    billing_cycle = Column(String(50), nullable=False)  # monthly, quarterly, yearly, custom
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active, inactive
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan", cascade="all, delete-orphan")
