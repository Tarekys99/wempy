"""
- نماذج Pydantic (الـ Schemas)
- حيث يتم تصميم سكيما لكل جدول بيانات لتحقق من صحة البيانات المضافة
- Validate Data Pydantic Before Insertion to Database
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr
from pydantic.types import UUID4
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    FName: str
    LName: str
    PhoneNumber: str = Field(..., pattern=r'^\d{11}$') # أرقام فقط 11 رقم بالضبط
    Email: Optional[EmailStr] = None

    @field_validator("PhoneNumber")
    @classmethod
    def validate_phone(cls, value):

         if not value.startswith( ("010", "011", "012", "015") ):
              raise ValueError("Phone number is not correct")
         return value

class UserCreate(UserBase):
    pass

class UserLogin(BaseModel):
    PhoneNumber: str = Field(..., pattern=r'^\d{11}$')
    @field_validator("PhoneNumber")
    @classmethod
    def validate_phone(cls, value):

         if not value.startswith( ("010", "011", "012", "015") ):
              raise ValueError("Phone number is not correct")
         return value

class UserUpdate(BaseModel):
    """
    تحديث معلومات المستخدم - جميع الحقول اختيارية
    يمكن تحديث حقل واحد أو أكثر
    """
    FName: Optional[str] = None
    LName: Optional[str] = None
    PhoneNumber: Optional[str] = Field(None, pattern=r'^\d{11}$')
    Email: Optional[EmailStr] = None

    @field_validator("PhoneNumber")
    @classmethod
    def validate_phone(cls, value):
        if value is not None:
            if not value.startswith( ("010", "011", "012", "015") ):
                raise ValueError("Phone number is not correct")
        return value

class UserResponse(UserBase):
    UserID: UUID4
    createdAt: datetime
    lastLogin: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

