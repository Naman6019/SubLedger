from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_plan_service
from app.schemas.plan import PlanCreate, PlanUpdate, PlanResponse
from app.services.plan_service import PlanService

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.post(
    "",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a subscription plan",
)
def create_plan(
    plan_in: PlanCreate,
    service: PlanService = Depends(get_plan_service),
) -> PlanResponse:
    return service.create_plan(plan_in)


@router.get(
    "",
    response_model=List[PlanResponse],
    summary="List plans",
)
def list_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status ('active', 'inactive')"),
    service: PlanService = Depends(get_plan_service),
) -> List[PlanResponse]:
    return service.list_plans(skip=skip, limit=limit, status=status)


@router.patch(
    "/{plan_id}",
    response_model=PlanResponse,
    summary="Update or deactivate a plan",
)
def update_plan(
    plan_id: int,
    plan_update: PlanUpdate,
    service: PlanService = Depends(get_plan_service),
) -> PlanResponse:
    return service.update_plan(plan_id, plan_update)
