from decimal import Decimal
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    assert resp.json()["service"] == "SubLedger"


def test_plans_api_crud_and_filter(client: TestClient):
    # Create active plan
    p1 = client.post(
        "/plans",
        json={
            "name": "Silver Monthly",
            "billing_cycle": "monthly",
            "price": 20.00,
            "currency": "USD",
            "status": "active",
        },
    ).json()

    # Create inactive plan
    p2 = client.post(
        "/plans",
        json={
            "name": "Gold Yearly",
            "billing_cycle": "yearly",
            "price": 200.00,
            "currency": "USD",
            "status": "inactive",
        },
    ).json()

    # List all plans
    all_plans = client.get("/plans").json()
    assert len(all_plans) == 2

    # Filter by status
    active_plans = client.get("/plans?status=active").json()
    assert len(active_plans) == 1
    assert active_plans[0]["id"] == p1["id"]

    # Update plan
    updated = client.patch(f"/plans/{p1['id']}", json={"description": "Updated description", "price": 22.50}).json()
    assert updated["description"] == "Updated description"
    assert Decimal(str(updated["price"])) == Decimal("22.50")


def test_customers_api_crud(client: TestClient):
    # Create customer
    c1 = client.post(
        "/customers",
        json={"name": "Acme Corp", "email": "contact@acme.com", "company_name": "Acme Inc"},
    ).json()

    # Get customer details
    fetched = client.get(f"/customers/{c1['id']}").json()
    assert fetched["id"] == c1["id"]
    assert fetched["name"] == "Acme Corp"
    assert fetched["email"] == "contact@acme.com"

    # List customers
    cust_list = client.get("/customers").json()
    assert len(cust_list) == 1


def test_subscriptions_listing_and_filtering(client: TestClient):
    cust1 = client.post("/customers", json={"name": "User 1", "email": "u1@test.com"}).json()
    cust2 = client.post("/customers", json={"name": "User 2", "email": "u2@test.com"}).json()
    plan1 = client.post(
        "/plans",
        json={"name": "Plan 1", "billing_cycle": "monthly", "price": 10.00, "currency": "USD"},
    ).json()
    plan2 = client.post(
        "/plans",
        json={"name": "Plan 2", "billing_cycle": "quarterly", "price": 25.00, "currency": "USD"},
    ).json()

    sub1 = client.post("/subscriptions", json={"customer_id": cust1["id"], "plan_id": plan1["id"]}).json()
    sub2 = client.post("/subscriptions", json={"customer_id": cust2["id"], "plan_id": plan2["id"]}).json()

    # Filter subscriptions by customer_id
    res_c1 = client.get(f"/subscriptions?customer_id={cust1['id']}").json()
    assert len(res_c1) == 1
    assert res_c1[0]["id"] == sub1["id"]

    # Filter subscriptions by plan_id
    res_p2 = client.get(f"/subscriptions?plan_id={plan2['id']}").json()
    assert len(res_p2) == 1
    assert res_p2[0]["id"] == sub2["id"]


def test_not_found_handling(client: TestClient):
    # 404 on non-existent plan
    resp_plan = client.get("/plans/99999")
    assert resp_plan.status_code in [404, 405]

    # 404 on non-existent customer
    resp_cust = client.get("/customers/99999")
    assert resp_cust.status_code == 404
    assert resp_cust.json()["error_type"] == "ENTITY_NOT_FOUND"

    # 404 on non-existent invoice
    resp_inv = client.get("/invoices/99999")
    assert resp_inv.status_code == 404
    assert resp_inv.json()["error_type"] == "ENTITY_NOT_FOUND"
