from typing import List
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_customer_service, get_ledger_service
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.schemas.ledger import LedgerEntryResponse
from app.services.customer_service import CustomerService
from app.services.ledger_service import LedgerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a customer",
)
def create_customer(
    customer_in: CustomerCreate,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    return service.create_customer(customer_in)


@router.get(
    "",
    response_model=List[CustomerResponse],
    summary="List customers",
)
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: CustomerService = Depends(get_customer_service),
) -> List[CustomerResponse]:
    return service.list_customers(skip=skip, limit=limit)


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Fetch customer details",
)
def get_customer(
    customer_id: int,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    return service.get_customer(customer_id)


@router.get(
    "/{customer_id}/ledger",
    response_model=List[LedgerEntryResponse],
    summary="Fetch customer ledger history",
)
def get_customer_ledger(
    customer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    customer_service: CustomerService = Depends(get_customer_service),
    ledger_service: LedgerService = Depends(get_ledger_service),
) -> List[LedgerEntryResponse]:
    # Ensure customer exists
    customer_service.get_customer(customer_id)
    return ledger_service.get_customer_ledger(customer_id, skip=skip, limit=limit)
