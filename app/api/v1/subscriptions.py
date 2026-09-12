from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_subscription_service
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.post(
    "",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a subscription",
)
def create_subscription(
    sub_in: SubscriptionCreate,
    service: SubscriptionService = Depends(get_subscription_service),
) -> SubscriptionResponse:
    return service.create_subscription(sub_in)


@router.get(
    "",
    response_model=List[SubscriptionResponse],
    summary="List subscriptions",
)
def list_subscriptions(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    plan_id: Optional[int] = Query(None, description="Filter by plan ID"),
    status: Optional[str] = Query(None, description="Filter by status ('active', 'cancelled', 'expired')"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: SubscriptionService = Depends(get_subscription_service),
) -> List[SubscriptionResponse]:
    return service.list_subscriptions(
        customer_id=customer_id,
        plan_id=plan_id,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/{subscription_id}/cancel",
    response_model=SubscriptionResponse,
    summary="Cancel a subscription",
)
def cancel_subscription(
    subscription_id: int,
    service: SubscriptionService = Depends(get_subscription_service),
) -> SubscriptionResponse:
    return service.cancel_subscription(subscription_id)
