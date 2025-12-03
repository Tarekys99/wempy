from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

#======================================
# Payment Schemas
#======================================
class PaymentBase(BaseSchema):
    PaymentName: str = Field(..., min_length=3, max_length=50)
    IsActive: bool = Field(default=True)

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    PaymentID: int
    model_config = ConfigDict(from_attributes=True)
