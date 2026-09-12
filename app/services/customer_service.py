from typing import List
from app.core.exceptions import EntityNotFoundException, ConflictException
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate


class CustomerService:
    def __init__(self, customer_repo: CustomerRepository):
        self.customer_repo = customer_repo

    def create_customer(self, customer_in: CustomerCreate) -> Customer:
        normalized_email = customer_in.email.strip().lower()
        existing = self.customer_repo.get_by_email(normalized_email)
        if existing:
            raise ConflictException(f"Customer with email '{normalized_email}' already exists.")

        customer = Customer(
            name=customer_in.name,
            email=normalized_email,
            company_name=customer_in.company_name,
            status=customer_in.status or "active",
        )
        return self.customer_repo.create(customer)

    def get_customer(self, customer_id: int) -> Customer:
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise EntityNotFoundException(f"Customer with id {customer_id} not found.")
        return customer

    def list_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        return self.customer_repo.list_all(skip=skip, limit=limit)
