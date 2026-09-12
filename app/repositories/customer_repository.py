from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository):
    def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        statement = select(Customer).where(Customer.id == customer_id)
        return self.db.scalars(statement).first()

    def get_by_email(self, email: str) -> Optional[Customer]:
        statement = select(Customer).where(Customer.email == email)
        return self.db.scalars(statement).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        statement = select(Customer).offset(skip).limit(limit)
        return list(self.db.scalars(statement).all())
