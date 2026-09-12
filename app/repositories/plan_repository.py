from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.plan import Plan
from app.repositories.base_repository import BaseRepository


class PlanRepository(BaseRepository):
    def create(self, plan: Plan) -> Plan:
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def get_by_id(self, plan_id: int) -> Optional[Plan]:
        statement = select(Plan).where(Plan.id == plan_id)
        return self.db.scalars(statement).first()

    def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Plan]:
        statement = select(Plan)
        if status:
            statement = statement.where(Plan.status == status)
        statement = statement.offset(skip).limit(limit)
        return list(self.db.scalars(statement).all())

    def update(self, plan: Plan, update_fields: dict) -> Plan:
        for key, value in update_fields.items():
            setattr(plan, key, value)
        self.db.commit()
        self.db.refresh(plan)
        return plan
