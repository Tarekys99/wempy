# orders_schema.py

from pydantic import BaseModel, Field, UUID4, model_validator
from datetime import datetime
from typing import List, Optional, Any
from decimal import Decimal
from enum import Enum


class OrderStatus(str, Enum):
    PREPARING = "preparing"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# =================================
#  Order Item Schemas
# =================================

class OrderItemCreate(BaseModel):
    VariantID: int = Field(..., gt=0)
    Quantity: int = Field(..., gt=0, le=100)
    CustomPrice: Optional[Decimal] = Field(None, ge=10, description="السعر المخصص (للمنتجات حسب الطلب) - الحد الأدنى 10 ج.م")

class ProductVariantInfo(BaseModel):
    VariantID: int
    ProductID: int
    Name: str = Field(..., description="اسم المنتج")
    SizeName: Optional[str] = Field(None, description="الحجم")
    TypeName: Optional[str] = Field(None, description="النوع")
    Price: Decimal = Field(..., description="سعر الوحدة")
    
    @model_validator(mode='before')
    @classmethod
    def extract_from_relationships(cls, data: Any) -> Any:
        """استخراج البيانات من العلاقات في ProductVariant Model"""
        if hasattr(data, 'VariantID'):
            # إذا كان data هو ProductVariant object
            return {
                'VariantID': data.VariantID,
                'ProductID': data.ProductID,
                'Name': data.products.Name if hasattr(data, 'products') and data.products else None,
                'SizeName': data.sizes.SizeName if hasattr(data, 'sizes') and data.sizes else None,
                'TypeName': data.types.TypeName if hasattr(data, 'types') and data.types else None,
                'Price': data.Price
            }
        return data
    
    class Config:
        from_attributes = True

class OrderItemResponse(BaseModel):
    OrderItemID: int
    OrderID: int
    VariantID: int
    Quantity: int
    UnitPrice: Decimal
    Subtotal: Decimal
    
    # product info
    product_variants: ProductVariantInfo = Field(..., description="معلومات المنتج")
    
    class Config:
        from_attributes = True

# =================================
#  Order Schemas
# =================================

class OrderCreate(BaseModel):

    UserID: UUID4 = Field(...)
    ShiftID: int = Field(..., gt=0)
    AddressID: int = Field(..., gt=0)
    PaymentID: int = Field(..., gt=0)
    OrderNotes: Optional[str] = Field(None, max_length=500)
    ExternalNotes: Optional[str] = Field(None, max_length=500)
    
    items: List[OrderItemCreate] = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="قائمة المنتجات تحتوى على منتج واحد على الأقل"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "UserID": "123e4567-e89b-12d3-a456-426614174000",
                "ShiftID": 1,
                "AddressID": 2,
                "PaymentID": 2,
                "OrderNotes": "بدون بصل من فضلك",
                "ExternalNotes": "ملاحظات خارجية",
                "items": [
                    {"VariantID": 101, "Quantity": 2},
                    {"VariantID": 205, "Quantity": 1},
                    {"VariantID": 150, "Quantity": 3}
                ]
            }
        }


class OrderResponse(BaseModel):
    OrderID: int
    OrderNumber: int = Field(...)

    UserID: UUID4
    AddressID: int
    PaymentID: int
    ShiftID: int
    
    # order information 
    OrderTimestamp: datetime = Field(..., description="وقت إنشاء الطلب")
    Status: OrderStatus = Field(..., alias="OrderStatus", description="حالة الطلب الحالية")
    OrderNotes: Optional[str] = None
    ExternalNotes: Optional[str] = None
    
    # order pricing
    DeliveryFee: Decimal = Field(..., description="رسوم التوصيل")
    TotalPrice: Decimal = Field(..., description="السعر الإجمالي")
    
    # Computed Properties (من Model)
    is_completed: bool = Field(..., description="هل تم توصيل الطلب؟")
    is_cancelled: bool = Field(..., description="هل تم إلغاء الطلب؟")
    
    # order items
    order_items: List[OrderItemResponse] = Field(..., description="قائمة المنتجات في الطلب")
    
    class Config:
        from_attributes = True


# =========================================
#  Simplified Response
# =========================================

class OrderListResponse(BaseModel):
    OrderID: int
    OrderNumber: int
    UserID: UUID4
    Status: OrderStatus = Field(..., alias="OrderStatus")
    TotalPrice: Decimal
    OrderTimestamp: datetime
    is_completed: bool
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "OrderID": 123,
                "OrderNumber": 5,
                "UserID": "123e4567-e89b-12d3-a456-426614174000",
                "Status": "preparing",
                "TotalPrice": 250.00,
                "OrderTimestamp": "2024-11-03T10:30:00",
                "is_completed": False
            }
        }