from decimal import Decimal
from typing import Optional, Tuple
from app.core.exceptions import EntityNotFoundException, BusinessRuleViolationException
from app.models.invoice import Invoice
from app.models.payment import PaymentAttempt
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.payment_attempt_repository import PaymentAttemptRepository
from app.services.ledger_service import LedgerService


class PaymentService:
    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        payment_attempt_repo: PaymentAttemptRepository,
        ledger_service: LedgerService,
    ):
        self.invoice_repo = invoice_repo
        self.payment_attempt_repo = payment_attempt_repo
        self.ledger_service = ledger_service

    def record_payment(
        self,
        invoice_id: int,
        amount: Decimal,
        status: str,
        provider_reference: Optional[str] = None,
        currency: str = "USD",
        failure_reason: Optional[str] = None,
    ) -> Tuple[PaymentAttempt, Invoice]:
        # Step 2: Fetch invoice
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise EntityNotFoundException(f"Invoice with id {invoice_id} not found.")

        # Step 3: Validate invoice exists and payment amount is valid
        if amount <= Decimal("0"):
            raise BusinessRuleViolationException("Payment amount must be greater than 0.")

        remaining_unpaid = invoice.amount_due - invoice.amount_paid

        # Business rule: A successful payment cannot exceed the remaining unpaid amount on the invoice.
        if status == "success":
            if remaining_unpaid <= Decimal("0"):
                raise BusinessRuleViolationException(
                    f"Invoice #{invoice_id} is already fully paid. Cannot accept further payments."
                )
            if amount > remaining_unpaid:
                raise BusinessRuleViolationException(
                    f"Payment amount {amount} exceeds remaining unpaid balance of {remaining_unpaid}."
                )

        # Step 4: Create payment attempt record
        payment_attempt = PaymentAttempt(
            invoice_id=invoice.id,
            amount=amount,
            currency=currency.upper(),
            status=status,
            provider_reference=provider_reference,
            failure_reason=failure_reason if status == "failed" else None,
        )
        created_attempt = self.payment_attempt_repo.create(payment_attempt)

        # Reference for traceability
        ref_id = provider_reference or f"PAY-{created_attempt.id}"

        # Step 5 & 6: Update invoice only on success; do not increase amount_paid on failure
        if status == "failed":
            # Business rule: Failed payment does not increase amount_paid
            # Step 7: Create payment_failure ledger entry
            self.ledger_service.record_entry(
                customer_id=invoice.customer_id,
                invoice_id=invoice.id,
                entry_type="payment_failure",
                amount=amount,
                currency=currency,
                reference_id=ref_id,
                description=f"Failed payment attempt #{created_attempt.id}: {failure_reason or 'declined'}",
            )
        else:
            # Payment succeeded
            new_amount_paid = invoice.amount_paid + amount
            # Business rule: A fully paid invoice moves to 'paid'; partial payment moves to 'partially_paid'
            if new_amount_paid >= invoice.amount_due:
                new_status = "paid"
            else:
                new_status = "partially_paid"

            invoice = self.invoice_repo.update_payment(
                invoice=invoice,
                amount_paid=new_amount_paid,
                status=new_status,
            )

            # Step 7: Create payment_success ledger entry
            self.ledger_service.record_entry(
                customer_id=invoice.customer_id,
                invoice_id=invoice.id,
                entry_type="payment_success",
                amount=amount,
                currency=currency,
                reference_id=ref_id,
                description=f"Successful payment attempt #{created_attempt.id} ({new_status})",
            )

        # Step 8: Return payment attempt and updated invoice status
        return created_attempt, invoice
