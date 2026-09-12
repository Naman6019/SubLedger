from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


class LedgerEntryResponse(BaseModel):
    id: int
    customer_id: int
    invoice_id: Optional[int] = None
    entry_type: Literal["invoice_created", "payment_success", "payment_failure"]
    amount: Decimal
    currency: str
    reference_id: str
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
