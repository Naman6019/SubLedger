from fastapi import APIRouter, Depends, status
from app.api.deps import get_payment_service
from app.schemas.payment import (
    PaymentRecordRequest,
    PaymentRecordResponse,
    PaymentAttemptResponse,
)
from app.schemas.invoice import InvoiceResponse
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/record",
    response_model=PaymentRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a payment attempt",
)
def record_payment(
    payment_in: PaymentRecordRequest,
    service: PaymentService = Depends(get_payment_service),
) -> PaymentRecordResponse:
    attempt, invoice = service.record_payment(
        invoice_id=payment_in.invoice_id,
        amount=payment_in.amount,
        status=payment_in.status,
        provider_reference=payment_in.provider_reference,
        currency=payment_in.currency,
        failure_reason=payment_in.failure_reason,
    )
    return PaymentRecordResponse(
        payment_attempt=PaymentAttemptResponse.model_validate(attempt),
        invoice=InvoiceResponse.model_validate(invoice),
    )
