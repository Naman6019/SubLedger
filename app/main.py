from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import (
    SubLedgerException,
    EntityNotFoundException,
    ConflictException,
    BusinessRuleViolationException,
    InvalidStateTransitionException,
)
from app.db.base import Base
from app.db.session import engine
from app.api.v1.router import api_router
# Ensure all models are imported so Base metadata knows about them
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "SubLedger is a modular SaaS billing and append-only ledger backend. "
        "It manages plans, customers, subscriptions, invoice generation, payment recording, "
        "and traceable ledger events with strict separation of concerns."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(EntityNotFoundException)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message, "error_type": "ENTITY_NOT_FOUND"},
    )


@app.exception_handler(ConflictException)
async def conflict_handler(request: Request, exc: ConflictException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message, "error_type": "CONFLICT"},
    )


@app.exception_handler(BusinessRuleViolationException)
async def business_rule_violation_handler(request: Request, exc: BusinessRuleViolationException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message, "error_type": "BUSINESS_RULE_VIOLATION"},
    )


@app.exception_handler(InvalidStateTransitionException)
async def invalid_state_handler(request: Request, exc: InvalidStateTransitionException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message, "error_type": "INVALID_STATE_TRANSITION"},
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


# Include both prefixed (/api/v1/...) and non-prefixed (/plans, ...) routes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router)
