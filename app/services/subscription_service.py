from datetime import datetime, timedelta, timezone
from typing import List, Optional
from app.core.exceptions import (
    EntityNotFoundException,
    BusinessRuleViolationException,
    ConflictException,
    InvalidStateTransitionException,
)
from app.models.subscription import Subscription
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.plan_repository import PlanRepository
from app.schemas.subscription import SubscriptionCreate


class SubscriptionService:
    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        customer_repo: CustomerRepository,
        plan_repo: PlanRepository,
    ):
        self.subscription_repo = subscription_repo
        self.customer_repo = customer_repo
        self.plan_repo = plan_repo

    def create_subscription(self, sub_in: SubscriptionCreate) -> Subscription:
        customer = self.customer_repo.get_by_id(sub_in.customer_id)
        if not customer:
            raise EntityNotFoundException(f"Customer with id {sub_in.customer_id} not found.")

        plan = self.plan_repo.get_by_id(sub_in.plan_id)
        if not plan:
            raise EntityNotFoundException(f"Plan with id {sub_in.plan_id} not found.")

        # Business Rule: A subscription cannot be created for an inactive plan.
        if plan.status != "active":
            raise BusinessRuleViolationException(
                f"Cannot create subscription: Plan '{plan.name}' (id: {plan.id}) is inactive."
            )

        # Business Rule: A customer cannot have two active subscriptions to the same plan.
        existing_active = self.subscription_repo.get_active_by_customer_and_plan(
            customer_id=sub_in.customer_id, plan_id=sub_in.plan_id
        )
        if existing_active:
            raise ConflictException(
                f"Customer {sub_in.customer_id} already has an active subscription to plan {sub_in.plan_id}."
            )

        start = sub_in.start_date or datetime.now(timezone.utc)
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)

        # Calculate period based on billing cycle
        days = 30
        if plan.billing_cycle == "monthly":
            days = 30
        elif plan.billing_cycle == "quarterly":
            days = 90
        elif plan.billing_cycle == "yearly":
            days = 365

        period_end = start + timedelta(days=days)

        subscription = Subscription(
            customer_id=sub_in.customer_id,
            plan_id=sub_in.plan_id,
            status="active",
            start_date=start,
            current_period_start=start,
            current_period_end=period_end,
            cancelled_at=None,
        )
        return self.subscription_repo.create(subscription)

    def get_subscription(self, subscription_id: int) -> Subscription:
        subscription = self.subscription_repo.get_by_id(subscription_id)
        if not subscription:
            raise EntityNotFoundException(f"Subscription with id {subscription_id} not found.")
        return subscription

    def list_subscriptions(
        self,
        customer_id: Optional[int] = None,
        plan_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Subscription]:
        return self.subscription_repo.list_all(
            customer_id=customer_id,
            plan_id=plan_id,
            status=status,
            skip=skip,
            limit=limit,
        )

    def cancel_subscription(self, subscription_id: int) -> Subscription:
        subscription = self.get_subscription(subscription_id)
        if subscription.status == "cancelled":
            raise InvalidStateTransitionException(
                f"Subscription {subscription_id} is already cancelled."
            )

        now = datetime.now(timezone.utc)
        return self.subscription_repo.update(
            subscription,
            {"status": "cancelled", "cancelled_at": now},
        )
