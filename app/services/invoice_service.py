from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional
from app.core.exceptions import EntityNotFoundException, BusinessRuleViolationException
from app.models.invoice import Invoice
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.plan_repository import PlanRepository
from app.services.ledger_service import LedgerService


class InvoiceService:
    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        plan_repo: PlanRepository,
        invoice_repo: InvoiceRepository,
        ledger_service: LedgerService,
    ):
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.invoice_repo = invoice_repo
        self.ledger_service = ledger_service

    def generate_invoice(
        self,
        subscription_id: int,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        status: str = "issued",
    ) -> Invoice:
        # Step 2 & 3: Fetch subscription and verify it exists and is active
        subscription = self.subscription_repo.get_by_id(subscription_id)
        if not subscription:
            raise EntityNotFoundException(f"Subscription with id {subscription_id} not found.")

        if subscription.status != "active":
            raise BusinessRuleViolationException(
                f"Cannot generate invoice: Subscription {subscription_id} is not active (current status: {subscription.status})."
            )

        # Step 4: Fetch plan details or plan price snapshot
        plan = self.plan_repo.get_by_id(subscription.plan_id)
        if not plan:
            raise EntityNotFoundException(f"Associated plan with id {subscription.plan_id} not found.")

        # Step 5: Calculate amount_due and billing period
        # Business rule: Invoice amount_due comes from plan price at the time invoice is generated
        amount_due = plan.price

        start = period_start or subscription.current_period_start
        end = period_end or subscription.current_period_end
        now = datetime.now(timezone.utc)
        due_date = now + timedelta(days=14)

        # Step 6: Create invoice with issued or draft status
        invoice = Invoice(
            subscription_id=subscription.id,
            customer_id=subscription.customer_id,
            amount_due=amount_due,
            amount_paid=Decimal("0.00"),
            currency=plan.currency,
            status=status if status in {"draft", "issued"} else "issued",
            period_start=start,
            period_end=end,
            due_date=due_date,
        )
        created_invoice = self.invoice_repo.create(invoice)

        # Step 7: LedgerService creates invoice_created ledger entry
        self.ledger_service.record_entry(
            customer_id=created_invoice.customer_id,
            invoice_id=created_invoice.id,
            entry_type="invoice_created",
            amount=created_invoice.amount_due,
            currency=created_invoice.currency,
            reference_id=f"INV-{created_invoice.id}",
            description=f"Invoice #{created_invoice.id} generated for subscription #{subscription.id}",
        )

        # Step 8: Return invoice response
        return created_invoice

    def get_invoice(self, invoice_id: int) -> Invoice:
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise EntityNotFoundException(f"Invoice with id {invoice_id} not found.")
        return invoice
