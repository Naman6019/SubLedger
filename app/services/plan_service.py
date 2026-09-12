from typing import List, Optional
from decimal import Decimal
from app.core.exceptions import EntityNotFoundException, BusinessRuleViolationException
from app.models.plan import Plan
from app.repositories.plan_repository import PlanRepository
from app.schemas.plan import PlanCreate, PlanUpdate


class PlanService:
    def __init__(self, plan_repo: PlanRepository):
        self.plan_repo = plan_repo

    def create_plan(self, plan_in: PlanCreate) -> Plan:
        if plan_in.price <= Decimal("0"):
            raise BusinessRuleViolationException("Plan price must be greater than 0.")

        plan = Plan(
            name=plan_in.name,
            description=plan_in.description,
            billing_cycle=plan_in.billing_cycle,
            price=plan_in.price,
            currency=plan_in.currency.upper(),
            status=plan_in.status,
        )
        return self.plan_repo.create(plan)

    def get_plan(self, plan_id: int) -> Plan:
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise EntityNotFoundException(f"Plan with id {plan_id} not found.")
        return plan

    def list_plans(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Plan]:
        return self.plan_repo.list_all(skip=skip, limit=limit, status=status)

    def update_plan(self, plan_id: int, plan_update: PlanUpdate) -> Plan:
        plan = self.get_plan(plan_id)

        update_data = plan_update.model_dump(exclude_unset=True)
        if "price" in update_data and update_data["price"] is not None:
            if update_data["price"] <= Decimal("0"):
                raise BusinessRuleViolationException("Plan price must be greater than 0.")

        if "currency" in update_data and update_data["currency"] is not None:
            update_data["currency"] = update_data["currency"].upper()

        return self.plan_repo.update(plan, update_data)
