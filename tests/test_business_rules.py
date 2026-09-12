from decimal import Decimal
import pytest
from fastapi.testclient import TestClient


def test_plan_price_must_be_greater_than_zero(client: TestClient):
    """
    Business Rule 1: Plan price must be greater than 0.
    """
    # 1a. Test price = 0
    resp_zero = client.post(
        "/plans",
        json={
            "name": "Zero Plan",
            "billing_cycle": "monthly",
            "price": 0.0,
            "currency": "USD",
        },
    )
    assert resp_zero.status_code in [400, 422]

    # 1b. Test price < 0
    resp_neg = client.post(
        "/plans",
        json={
            "name": "Negative Plan",
            "billing_cycle": "monthly",
            "price": -15.50,
            "currency": "USD",
        },
    )
    assert resp_neg.status_code in [400, 422]

    # 1c. Test valid price > 0
    resp_valid = client.post(
        "/plans",
        json={
            "name": "Valid Plan",
            "billing_cycle": "monthly",
            "price": 49.99,
            "currency": "USD",
        },
    )
    assert resp_valid.status_code == 201
    assert Decimal(str(resp_valid.json()["price"])) == Decimal("49.99")


def test_customer_email_must_be_unique(client: TestClient):
    """
    Business Rule 2: Customer email must be unique.
    """
    customer_payload = {
        "name": "Alice Corp",
        "email": "alice@subledger.io",
        "company_name": "Alice Inc",
    }
    # 2a. First customer creation should succeed
    resp1 = client.post("/customers", json=customer_payload)
    assert resp1.status_code == 201
    assert resp1.json()["email"] == "alice@subledger.io"

    # 2b. Second customer creation with same email should fail with 409 Conflict
    resp2 = client.post("/customers", json=customer_payload)
    assert resp2.status_code == 409
    assert "already exists" in resp2.json()["detail"].lower()


def test_subscription_cannot_be_created_for_inactive_plan(client: TestClient):
    """
    Business Rule 3: A subscription cannot be created for an inactive plan.
    """
    # Create customer
    cust_resp = client.post(
        "/customers",
        json={"name": "Bob", "email": "bob@example.com"},
    )
    cust_id = cust_resp.json()["id"]

    # Create inactive plan
    plan_resp = client.post(
        "/plans",
        json={
            "name": "Legacy Archival Plan",
            "billing_cycle": "monthly",
            "price": 19.99,
            "currency": "USD",
            "status": "inactive",
        },
    )
    plan_id = plan_resp.json()["id"]

    # Try subscribing to inactive plan
    sub_resp = client.post(
        "/subscriptions",
        json={"customer_id": cust_id, "plan_id": plan_id},
    )
    assert sub_resp.status_code == 400
    assert "inactive" in sub_resp.json()["detail"].lower()


def test_no_duplicate_active_subscriptions_to_same_plan(client: TestClient):
    """
    Business Rule 4: A customer cannot have two active subscriptions to the same plan in the base version.
    """
    # Setup customer and plan
    cust_resp = client.post(
        "/customers",
        json={"name": "Charlie", "email": "charlie@example.com"},
    )
    cust_id = cust_resp.json()["id"]

    plan_resp = client.post(
        "/plans",
        json={
            "name": "Pro Tier",
            "billing_cycle": "monthly",
            "price": 99.00,
            "currency": "USD",
        },
    )
    plan_id = plan_resp.json()["id"]

    # First active subscription
    sub1 = client.post(
        "/subscriptions",
        json={"customer_id": cust_id, "plan_id": plan_id},
    )
    assert sub1.status_code == 201
    assert sub1.json()["status"] == "active"

    # Second active subscription attempt to same plan should fail with 409 Conflict
    sub2 = client.post(
        "/subscriptions",
        json={"customer_id": cust_id, "plan_id": plan_id},
    )
    assert sub2.status_code == 409
    assert "already has an active subscription" in sub2.json()["detail"].lower()


def test_invoice_amount_due_comes_from_plan_price_snapshot(client: TestClient):
    """
    Business Rule 5: Invoice amount_due should come from the plan price at the time invoice is generated.
    """
    # Setup customer and plan
    cust = client.post("/customers", json={"name": "David", "email": "david@example.com"}).json()
    plan = client.post(
        "/plans",
        json={"name": "Basic", "billing_cycle": "monthly", "price": 25.00, "currency": "USD"},
    ).json()

    sub = client.post(
        "/subscriptions",
        json={"customer_id": cust["id"], "plan_id": plan["id"]},
    ).json()

    # Generate invoice when plan price is 25.00
    inv = client.post(
        "/invoices/generate",
        json={"subscription_id": sub["id"]},
    ).json()
    assert Decimal(str(inv["amount_due"])) == Decimal("25.00")
    assert Decimal(str(inv["amount_paid"])) == Decimal("0.00")
    assert inv["status"] == "issued"

    # Now update plan price to 35.00
    client.patch(f"/plans/{plan['id']}", json={"price": 35.00})

    # Historical invoice should retain the 25.00 snapshot
    fetched_inv = client.get(f"/invoices/{inv['id']}").json()
    assert Decimal(str(fetched_inv["amount_due"])) == Decimal("25.00")

    # A newly generated invoice now takes the updated price snapshot 35.00
    inv2 = client.post(
        "/invoices/generate",
        json={"subscription_id": sub["id"]},
    ).json()
    assert Decimal(str(inv2["amount_due"])) == Decimal("35.00")


def test_successful_payment_cannot_exceed_unpaid_amount(client: TestClient):
    """
    Business Rule 6: A successful payment cannot exceed the remaining unpaid amount on the invoice.
    """
    # Setup
    cust = client.post("/customers", json={"name": "Eve", "email": "eve@example.com"}).json()
    plan = client.post(
        "/plans",
        json={"name": "Starter", "billing_cycle": "monthly", "price": 100.00, "currency": "USD"},
    ).json()
    sub = client.post("/subscriptions", json={"customer_id": cust["id"], "plan_id": plan["id"]}).json()
    inv = client.post("/invoices/generate", json={"subscription_id": sub["id"]}).json()

    # Try paying 150 on an invoice with amount_due = 100
    overpayment = client.post(
        "/payments/record",
        json={
            "invoice_id": inv["id"],
            "amount": 150.00,
            "currency": "USD",
            "status": "success",
            "provider_reference": "TXN_OVERPAY_1",
        },
    )
    assert overpayment.status_code == 400
    assert "exceeds remaining unpaid balance" in overpayment.json()["detail"].lower()


def test_payment_status_transitions_partial_and_full(client: TestClient):
    """
    Business Rule 7: A fully paid invoice should move to paid status;
    a partial payment should move to partially_paid status.
    """
    # Setup invoice of 100.00
    cust = client.post("/customers", json={"name": "Frank", "email": "frank@example.com"}).json()
    plan = client.post(
        "/plans",
        json={"name": "Business", "billing_cycle": "monthly", "price": 100.00, "currency": "USD"},
    ).json()
    sub = client.post("/subscriptions", json={"customer_id": cust["id"], "plan_id": plan["id"]}).json()
    inv = client.post("/invoices/generate", json={"subscription_id": sub["id"]}).json()

    # 7a. Partial payment of 40.00
    pay1 = client.post(
        "/payments/record",
        json={
            "invoice_id": inv["id"],
            "amount": 40.00,
            "currency": "USD",
            "status": "success",
            "provider_reference": "TXN_PARTIAL_40",
        },
    )
    assert pay1.status_code == 201
    res1 = pay1.json()
    assert res1["invoice"]["status"] == "partially_paid"
    assert Decimal(str(res1["invoice"]["amount_paid"])) == Decimal("40.00")

    # 7b. Second partial payment of 60.00 (completing total 100.00)
    pay2 = client.post(
        "/payments/record",
        json={
            "invoice_id": inv["id"],
            "amount": 60.00,
            "currency": "USD",
            "status": "success",
            "provider_reference": "TXN_FULL_60",
        },
    )
    assert pay2.status_code == 201
    res2 = pay2.json()
    assert res2["invoice"]["status"] == "paid"
    assert Decimal(str(res2["invoice"]["amount_paid"])) == Decimal("100.00")

    # 7c. Further payment attempt should fail since invoice is fully paid
    pay3 = client.post(
        "/payments/record",
        json={
            "invoice_id": inv["id"],
            "amount": 10.00,
            "currency": "USD",
            "status": "success",
            "provider_reference": "TXN_EXTRA_10",
        },
    )
    assert pay3.status_code == 400
    assert "already fully paid" in pay3.json()["detail"].lower()


def test_failed_payment_does_not_increase_amount_paid(client: TestClient):
    """
    Business Rule 8: A failed payment should not increase amount_paid and should log failure reason.
    """
    cust = client.post("/customers", json={"name": "Grace", "email": "grace@example.com"}).json()
    plan = client.post(
        "/plans",
        json={"name": "Standard", "billing_cycle": "monthly", "price": 50.00, "currency": "USD"},
    ).json()
    sub = client.post("/subscriptions", json={"customer_id": cust["id"], "plan_id": plan["id"]}).json()
    inv = client.post("/invoices/generate", json={"subscription_id": sub["id"]}).json()

    # Attempt failed payment
    fail_resp = client.post(
        "/payments/record",
        json={
            "invoice_id": inv["id"],
            "amount": 50.00,
            "currency": "USD",
            "status": "failed",
            "provider_reference": "TXN_FAILED_001",
            "failure_reason": "Insufficient funds on card",
        },
    )
    assert fail_resp.status_code == 201
    result = fail_resp.json()
    assert result["payment_attempt"]["status"] == "failed"
    assert result["payment_attempt"]["failure_reason"] == "Insufficient funds on card"
    # Invoice amount_paid must not increase
    assert Decimal(str(result["invoice"]["amount_paid"])) == Decimal("0.00")
    assert result["invoice"]["status"] == "issued"


def test_ledger_entries_append_only_and_traceable(client: TestClient):
    """
    Business Rule 9: Ledger entries should be append-only and traceable through reference_id.
    """
    cust = client.post("/customers", json={"name": "Hannah", "email": "hannah@example.com"}).json()
    plan = client.post(
        "/plans",
        json={"name": "Enterprise", "billing_cycle": "yearly", "price": 1200.00, "currency": "USD"},
    ).json()
    sub = client.post("/subscriptions", json={"customer_id": cust["id"], "plan_id": plan["id"]}).json()

    # 1. Generating invoice should create an 'invoice_created' ledger entry
    inv = client.post("/invoices/generate", json={"subscription_id": sub["id"]}).json()

    # 2. Failed payment attempt should create 'payment_failure' ledger entry
    client.post(
        "/payments/record",
        json={
            "invoice_id": inv["id"],
            "amount": 1200.00,
            "currency": "USD",
            "status": "failed",
            "provider_reference": "TXN_DECLINED",
            "failure_reason": "Expired card",
        },
    )

    # 3. Successful payment should create 'payment_success' ledger entry
    client.post(
        "/payments/record",
        json={
            "invoice_id": inv["id"],
            "amount": 1200.00,
            "currency": "USD",
            "status": "success",
            "provider_reference": "TXN_APPROVED",
        },
    )

    # 4. Fetch customer ledger history
    ledger_resp = client.get(f"/customers/{cust['id']}/ledger")
    assert ledger_resp.status_code == 200
    entries = ledger_resp.json()

    assert len(entries) == 3
    assert entries[0]["entry_type"] == "invoice_created"
    assert entries[0]["reference_id"] == f"INV-{inv['id']}"
    assert Decimal(str(entries[0]["amount"])) == Decimal("1200.00")

    assert entries[1]["entry_type"] == "payment_failure"
    assert entries[1]["reference_id"] == "TXN_DECLINED"

    assert entries[2]["entry_type"] == "payment_success"
    assert entries[2]["reference_id"] == "TXN_APPROVED"


def test_subscription_cancellation_lifecycle(client: TestClient):
    """
    Lifecycle test: Subscription cancellation and preventing duplicate cancellations or invalid actions.
    """
    cust = client.post("/customers", json={"name": "Ian", "email": "ian@example.com"}).json()
    plan = client.post(
        "/plans",
        json={"name": "Basic Monthly", "billing_cycle": "monthly", "price": 15.00, "currency": "USD"},
    ).json()
    sub = client.post("/subscriptions", json={"customer_id": cust["id"], "plan_id": plan["id"]}).json()

    # Cancel subscription
    cancel_resp = client.patch(f"/subscriptions/{sub['id']}/cancel")
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"
    assert cancel_resp.json()["cancelled_at"] is not None

    # Try cancelling again -> should fail
    dup_cancel = client.patch(f"/subscriptions/{sub['id']}/cancel")
    assert dup_cancel.status_code == 400
    assert "already cancelled" in dup_cancel.json()["detail"].lower()

    # Inactive/cancelled subscription cannot generate new invoices
    inv_resp = client.post("/invoices/generate", json={"subscription_id": sub["id"]})
    assert inv_resp.status_code == 400
    assert "not active" in inv_resp.json()["detail"].lower()
