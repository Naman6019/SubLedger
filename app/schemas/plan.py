from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


class PlanBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Plan name")
    description: Optional[str] = Field(None, max_length=255, description="Plan description")
    billing_cycle: Literal["monthly", "quarterly", "yearly", "custom"] = Field(
        ..., description="Billing cycle: monthly, quarterly, yearly, or custom"
    )
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Plan price must be greater than 0")
    currency: str = Field("USD", min_length=3, max_length=10, description="Three-letter currency code")
    status: Literal["active", "inactive"] = Field("active", description="Status of the plan")


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    billing_cycle: Optional[Literal["monthly", "quarterly", "yearly", "custom"]] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    currency: Optional[str] = Field(None, min_length=3, max_length=10)
    status: Optional[Literal["active", "inactive"]] = None


class PlanResponse(PlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
