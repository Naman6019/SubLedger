from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Customer full name")
    email: str = Field(
        ...,
        pattern=EMAIL_REGEX,
        description="Customer unique email address",
    )
    company_name: Optional[str] = Field(None, max_length=100, description="Company name")


class CustomerCreate(CustomerBase):
    status: Optional[Literal["active", "inactive"]] = "active"


class CustomerResponse(CustomerBase):
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
