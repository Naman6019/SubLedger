# SubLedger — Simplified Billing & Financial Ledger Backend

SubLedger is a clean, modular SaaS billing and financial ledger backend designed with **Low-Level Design (LLD)** rigor and strict separation of concerns. It implements the complete subscription lifecycle, period-accurate invoice generation with price snapshots, payment recording (partial and full), and an append-only, traceable accounting ledger.

---

## Architecture Highlights

- **Framework**: FastAPI (Python 3.11+)
- **ORM & Database**: SQLAlchemy 2.0 with SQLite (default) and PostgreSQL compatibility
- **Validation & Schemas**: Pydantic v2
- **Testing**: Pytest with isolated in-memory SQLite databases
- **Design Patterns**:
  - **Repository Pattern**: All database read/write queries isolated in dedicated repository classes.
  - **Service Layer Pattern**: Business rules and multi-entity orchestrations encapsulated in services.
  - **Dependency Injection**: Dependencies injected cleanly via FastAPI `Depends()`.
  - **Append-Only Ledger**: Immutable audit log guaranteed by omitting update/delete primitives.

For in-depth architectural diagrams, ERD, and flow sequences, see **[DESIGN.md](./DESIGN.md)**.

---

## Project Structure

```
SubLedger/
├── app/
│   ├── api/
│   │   ├── deps.py             # Dependency injection providers (Repos & Services)
│   │   └── v1/
│   │       ├── plans.py         # /plans routes
│   │       ├── customers.py     # /customers routes
│   │       ├── subscriptions.py # /subscriptions routes
│   │       ├── invoices.py      # /invoices routes
│   │       ├── payments.py      # /payments routes
│   │       └── router.py        # Aggregated v1 API router
│   ├── core/
│   │   ├── config.py           # Pydantic Settings & environment configuration
│   │   └── exceptions.py       # Domain-level exceptions
│   ├── db/
│   │   ├── base.py             # Declarative Base
│   │   └── session.py          # SQLAlchemy engine and SessionLocal
│   ├── models/                 # SQLAlchemy 2.0 Declarative Models
│   │   ├── plan.py
│   │   ├── customer.py
│   │   ├── subscription.py
│   │   ├── invoice.py
│   │   ├── payment.py
│   │   └── ledger.py
│   ├── repositories/           # Data Access Layer (Repository Pattern)
│   │   ├── base_repository.py
│   │   ├── plan_repository.py
│   │   ├── customer_repository.py
│   │   ├── subscription_repository.py
│   │   ├── invoice_repository.py
│   │   ├── payment_attempt_repository.py
│   │   └── ledger_repository.py  # Strictly append-only
│   ├── schemas/                # Pydantic Data Transfer Objects (DTOs)
│   │   ├── plan.py
│   │   ├── customer.py
│   │   ├── subscription.py
│   │   ├── invoice.py
│   │   ├── payment.py
│   │   └── ledger.py
│   └── services/               # Business Logic Layer (Service Layer Pattern)
│       ├── plan_service.py
│       ├── customer_service.py
│       ├── subscription_service.py
│       ├── invoice_service.py
│       ├── payment_service.py
│       └── ledger_service.py
│   └── main.py                 # FastAPI app, lifespan, CORS, and exception handlers
├── tests/
│   ├── conftest.py             # In-memory test DB fixture and TestClient
│   ├── test_business_rules.py  # 10 tests for all mandatory business rules
│   └── test_api_endpoints.py   # API integration and filtering tests
├── .env.example
├── .gitignore
├── DESIGN.md                   # Detailed Low-Level Design documentation
├── Dockerfile                  # Production container definition
├── docker-compose.yml          # Containerized orchestration
├── openapi.json                # Exported OpenAPI/Swagger specification
├── SubLedger.postman_collection.json # Ready-to-import Postman collection
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Quickstart & Local Setup

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.11 & 3.13)
- `pip` or virtual environment manager

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone <repository-url>
cd SubLedger

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
```

### 4. Run the Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **Interactive Swagger Docs (Live)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Alternate Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema (JSON)**: [`openapi.json`](./openapi.json) or [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **Postman Collection**: [`SubLedger.postman_collection.json`](./SubLedger.postman_collection.json) (Ready to import into Postman)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## Docker Deployment

You can run SubLedger with Docker and Docker Compose:

```bash
# Build and start container
docker-compose up --build -d

# View container logs
docker-compose logs -f

# Run tests inside the container
docker-compose exec api pytest

# Stop container
docker-compose down
```

---

## Complete API Reference

All routes are available at both root `/` and `/api/v1/` prefixes for flexibility.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/plans` | Create a new subscription plan |
| `GET` | `/plans` | List plans (optional `?status=active`) |
| `PATCH` | `/plans/{plan_id}` | Update plan details or deactivate a plan |
| `POST` | `/customers` | Register a new customer |
| `GET` | `/customers` | List registered customers |
| `GET` | `/customers/{customer_id}` | Fetch customer profile |
| `POST` | `/subscriptions` | Subscribe a customer to a plan |
| `GET` | `/subscriptions` | List subscriptions (filter by customer, plan, status) |
| `PATCH` | `/subscriptions/{subscription_id}/cancel` | Cancel an active subscription |
| `POST` | `/invoices/generate` | Generate invoice for an active subscription |
| `GET` | `/invoices/{invoice_id}` | Fetch invoice details and payment progress |
| `POST` | `/payments/record` | Record payment attempt (handles success & failure) |
| `GET` | `/customers/{customer_id}/ledger` | Fetch complete audit ledger history for customer |

---

## End-to-End Workflow Examples (cURL)

### 1. Create a Plan
```bash
curl -X POST "http://localhost:8000/plans" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Scale Pro",
    "description": "High-tier plan for growing teams",
    "billing_cycle": "monthly",
    "price": 99.00,
    "currency": "USD",
    "status": "active"
  }'
```

### 2. Create a Customer
```bash
curl -X POST "http://localhost:8000/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Starlight Technologies",
    "email": "billing@starlight.io",
    "company_name": "Starlight Inc"
  }'
```

### 3. Create a Subscription
```bash
curl -X POST "http://localhost:8000/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "plan_id": 1
  }'
```

### 4. Generate an Invoice
```bash
curl -X POST "http://localhost:8000/invoices/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "subscription_id": 1
  }'
```

### 5. Record a Successful Partial Payment
```bash
curl -X POST "http://localhost:8000/payments/record" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": 1,
    "amount": 49.00,
    "currency": "USD",
    "status": "success",
    "provider_reference": "ch_stripe_001"
  }'
```

### 6. Record Remaining Payment (Full Settlement)
```bash
curl -X POST "http://localhost:8000/payments/record" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": 1,
    "amount": 50.00,
    "currency": "USD",
    "status": "success",
    "provider_reference": "ch_stripe_002"
  }'
```

### 7. Inspect Customer Financial Ledger History
```bash
curl -X GET "http://localhost:8000/customers/1/ledger"
```

---

## Business Rules Enforcement

| # | Business Rule | Enforced At |
| :- | :--- | :--- |
| 1 | Plan price must be > 0 | `PlanCreate` schema validation (`gt=0`) & `PlanService` |
| 2 | Customer email must be unique | Database unique constraint & `CustomerService` pre-check |
| 3 | Subscription cannot be created for an inactive plan | `SubscriptionService` checks `plan.status == 'active'` |
| 4 | No duplicate active subscription to the same plan | `SubscriptionService` queries active subscription before creation |
| 5 | Invoice `amount_due` snapshots plan price | `InvoiceService` takes snapshot at generation instant |
| 6 | Payment cannot exceed remaining unpaid balance | `PaymentService` enforces `amount <= amount_due - amount_paid` |
| 7 | Full payment -> `paid`, Partial payment -> `partially_paid` | `PaymentService` computes balance and advances invoice status |
| 8 | Failed payment does not increase `amount_paid` | `PaymentService` logs failure reason without updating invoice balance |
| 9 | Ledger entries are strictly append-only and traceable | `LedgerRepository` has no `update` or `delete` methods |

---

## Running Automated Tests

SubLedger contains a comprehensive suite of unit and integration tests covering all business rules and edge cases.

```bash
# Run pytest with verbose reporting
pytest -v
```

### Test Suite Summary:
- `test_plan_price_must_be_greater_than_zero`: Validates positive pricing invariant.
- `test_customer_email_must_be_unique`: Verifies email uniqueness conflict prevention (HTTP 409).
- `test_subscription_cannot_be_created_for_inactive_plan`: Prevents subscribing to inactive tiers.
- `test_no_duplicate_active_subscriptions_to_same_plan`: Enforces single active subscription constraint.
- `test_invoice_amount_due_comes_from_plan_price_snapshot`: Verifies price freeze behavior.
- `test_successful_payment_cannot_exceed_unpaid_amount`: Rejects overpayment attempts.
- `test_payment_status_transitions_partial_and_full`: Verifies status transitions (`issued` -> `partially_paid` -> `paid`).
- `test_failed_payment_does_not_increase_amount_paid`: Verifies failure recording and isolation.
- `test_ledger_entries_append_only_and_traceable`: Confirms immutable ledger audit trail.
- `test_subscription_cancellation_lifecycle`: Tests cancellation transitions and prevention of duplicate cancels.
- `test_health_check`: Verifies system health probe.
- `test_plans_api_crud_and_filter`: Verifies plan listing, pagination, and status filters.
- `test_customers_api_crud`: Verifies customer lookup and listing.
- `test_subscriptions_listing_and_filtering`: Verifies multi-parameter subscription filtering.
- `test_not_found_handling`: Validates proper HTTP 404 responses for missing entities.

---

## Assumptions and Limitations

### Assumptions
1. **Currency Matching**: All operations default to `USD`. In a multi-currency extension, exchange rates and currency normalization services would be injected.
2. **Fixed Billing Windows**: Unless explicitly overridden via the API payload, standard cycle durations are 30 days for monthly, 90 days for quarterly, and 365 days for yearly plans.
3. **Traceability**: All external payment references (`provider_reference`) or internal identifiers (`INV-{id}`, `PAY-{id}`) are stored on ledger entries to facilitate bi-directional reconciliation.

### Limitations (Design Scope Boundaries)
1. **No External Payment Gateway SDK**: Real payment gateways (Stripe, Razorpay, Adyen) are external to this core domain model. Payment attempts are recorded via API callbacks/webhooks.
2. **No Proration Engine**: Subscription upgrades/downgrades with mid-cycle proration credits are omitted in this base version to keep the domain model focused.
3. **No Auth/RBAC**: Authentication and JWT/OAuth2 RBAC are omitted as per product scope guidelines.
