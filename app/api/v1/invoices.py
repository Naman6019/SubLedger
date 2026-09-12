from fastapi import APIRouter, Depends, status
from app.api.deps import get_invoice_service
from app.schemas.invoice import InvoiceGenerateRequest, InvoiceResponse
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post(
    "/generate",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate invoice for a subscription",
)
def generate_invoice(
    invoice_req: InvoiceGenerateRequest,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceResponse:
    return service.generate_invoice(
        subscription_id=invoice_req.subscription_id,
        period_start=invoice_req.period_start,
        period_end=invoice_req.period_end,
        status=invoice_req.status or "issued",
    )


@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Fetch invoice details",
)
def get_invoice(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceResponse:
    return service.get_invoice(invoice_id)
