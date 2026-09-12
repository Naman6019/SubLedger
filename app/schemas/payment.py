from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.invoice import InvoiceResponse


class PaymentRecordRequest(BaseModel):
    invoice_id: int = Field(..., gt=0, description="Invoice ID being paid")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Payment amount must be greater than 0")
    currency: str = Field("USD", min_length=3, max_length=10, description="Currency code")
    status: Literal["success", "failed"] = Field(..., description="Status of payment attempt: success or failed")
    provider_reference: Optional[str] = Field(None, max_length=100, description="Reference code from payment provider")
    failure_reason: Optional[str] = Field(None, max_length=255, description="Reason for failure if status is failed")


class PaymentAttemptResponse(BaseModel):
    id: int
    invoice_id: int
    amount: Decimal
    currency: str
    status: Literal["success", "failed"]
    provider_reference: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentRecordResponse(BaseModel):
    payment_attempt: PaymentAttemptResponse
    invoice: InvoiceResponse

    model_config = ConfigDict(from_attributes=True)
