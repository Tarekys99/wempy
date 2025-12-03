from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.types import UUID4
from decimal import Decimal
from typing import Optional, List

class BaseSchema(BaseModel):
     model_config = ConfigDict(from_attributes=True)

#======================================
# Address Schemas
#======================================
class AddressBase(BaseSchema):
    """Base schema with all address fields (without IDs)"""
    RecipientName: str = Field(..., min_length=3, max_length=50)
    Street: str = Field(..., min_length=3, max_length=50)
    Building: str = Field(..., min_length=1, max_length=50)
    City: str = Field(..., min_length=2, max_length=50)
    RecipientPhone: str = Field(..., pattern=r'^\d{11}$')
    Phone2: Optional[str] = Field(None, pattern=r'^\d{11}$')

    DeliveryNotes: Optional[str] = Field(None, min_length=1, max_length=500)
    ZoneID: int = Field(..., gt=0)

    @field_validator("RecipientPhone")
    @classmethod
    def validate_phone(cls, value):
         if not value.startswith(("010", "011", "012", "015")):
              raise ValueError("رقم الهاتف غير صحيح")
         return value

    @field_validator("Phone2", mode="before")
    @classmethod
    def validate_phone2(cls, v):
        if v == "" or v is None:
            return None
        if len(v) != 11 or not v.isdigit():
            raise ValueError("رقم الهاتف يجب أن يكون 11 رقم")
        if not v.startswith(("010", "011", "012", "015")):
            raise ValueError("رقم الهاتف غير صحيح")
        return v

    @field_validator("DeliveryNotes", mode="before")
    @classmethod
    def validate_delivery_notes(cls, v):
        if v == "" or v is None:
            return None
        return v


class AddressCreate(AddressBase):
    """Schema for creating a new address (UserID comes from session)"""
    pass

class AddressUpdate(BaseSchema):
    """Schema for updating an existing address (all fields optional)"""
    RecipientName: Optional[str] = Field(None, min_length=3, max_length=50)
    Street: Optional[str] = Field(None, min_length=3, max_length=50)
    Building: Optional[str] = Field(None, min_length=1, max_length=50)
    City: Optional[str] = Field(None, min_length=2, max_length=50)
    
    RecipientPhone: Optional[str] = Field(None, pattern=r'^\d{11}$')
    Phone2: Optional[str] = Field(None, pattern=r'^\d{11}$')
    DeliveryNotes: Optional[str] = Field(None, min_length=1, max_length=500)
    ZoneID: Optional[int] = Field(None, gt=0)

    @field_validator("RecipientPhone")
    @classmethod
    def validate_phone_update(cls, value):
        if value and not value.startswith(("010", "011", "012", "015")):
            raise ValueError("رقم الهاتف غير صحيح")
        return value
        
    @field_validator("Phone2", mode="before")
    @classmethod
    def validate_phone2_update(cls, v):
        if v == "" or v is None:
            return None
        if len(v) != 11 or not v.isdigit():
            raise ValueError("رقم الهاتف يجب أن يكون 11 رقم")
        if not v.startswith(("010", "011", "012", "015")):
            raise ValueError("رقم الهاتف غير صحيح")
        return v

    @field_validator("DeliveryNotes", mode="before")
    @classmethod
    def validate_delivery_notes_update(cls, v):
        if v == "" or v is None:
            return None
        return v

class AddressResponse(AddressBase):
    AddressID: int
    UserID: UUID4
    DeliveryNotes: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class AddressWithZone(AddressResponse):
    delivery_zone: "ZoneResponse"

#======================================
# DeliveryZone Schemas
#======================================
class ZoneBase(BaseSchema):
    ZoneName: str = Field(..., min_length=2, max_length=100)
    DeliveryCost: Decimal = Field(..., gt=0, decimal_places=2)

class ZoneCreate(ZoneBase):
    pass

class ZoneUpdate(BaseSchema):
    # admin only (all fields optionals)
    ZoneName: Optional[str] = Field(None, min_length=2, max_length=100)
    DeliveryCost: Optional[Decimal] = Field(None, gt=0, decimal_places=2)

class ZoneResponse(ZoneBase):
    ZoneID: int
    
    model_config = ConfigDict(from_attributes=True)

class ZoneWithAddresses(ZoneResponse):
    addresses: List[AddressResponse] = []
