from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.subscription import Subscription
from app.repositories.base_repository import BaseRepository


class SubscriptionRepository(BaseRepository):
    def create(self, subscription: Subscription) -> Subscription:
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def get_by_id(self, subscription_id: int) -> Optional[Subscription]:
        statement = select(Subscription).where(Subscription.id == subscription_id)
        return self.db.scalars(statement).first()

    def get_active_by_customer_and_plan(self, customer_id: int, plan_id: int) -> Optional[Subscription]:
        statement = select(Subscription).where(
            Subscription.customer_id == customer_id,
            Subscription.plan_id == plan_id,
            Subscription.status == "active",
        )
        return self.db.scalars(statement).first()

    def list_all(
        self,
        customer_id: Optional[int] = None,
        plan_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Subscription]:
        statement = select(Subscription)
        if customer_id is not None:
            statement = statement.where(Subscription.customer_id == customer_id)
        if plan_id is not None:
            statement = statement.where(Subscription.plan_id == plan_id)
        if status is not None:
            statement = statement.where(Subscription.status == status)
        statement = statement.offset(skip).limit(limit)
        return list(self.db.scalars(statement).all())

    def update(self, subscription: Subscription, update_fields: dict) -> Subscription:
        for key, value in update_fields.items():
            setattr(subscription, key, value)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
