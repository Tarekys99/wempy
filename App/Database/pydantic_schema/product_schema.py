from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional, List

class BaseSchema(BaseModel):
     model_config = ConfigDict(from_attributes=True)

#======================================
# Category Schemas
#======================================
class CategoryBase(BaseSchema): # سكيما أساسية فيها كل الحقول
     CategoryName: str = Field(...,min_length=3, max_length=50)

class CategoryCreate(CategoryBase): # انشاء فئة جديد
     pass

class CategoryUpdate(BaseSchema): # تحديث فئة موجودة
     CategoryName: Optional[str] = Field(None, min_length=3, max_length=50)

class CategoryResponse(CategoryBase): # => عرض الموجودة في الحقول كلها + أي دي
     CategoryID: int

     model_config = ConfigDict(from_attributes=True)

class CategoryWithProducts(CategoryResponse):
    products: List["ProductResponse"] = [] 
    # variable 'products' --> يشير لأسم العلاقة بين الجدولين في db model files
#======================================
# Products Schemas
#======================================
class ProductBase(BaseSchema):

     CategoryID: int = Field(..., gt=0)
     Name: str = Field(...,min_length=3, max_length=50)
     Description: Optional[str] = Field(None, min_length=1, max_length=200)
     ImageUrl: str = Field(..., min_length=1, max_length=255)
     
class ProductCreate(ProductBase):
     pass

class ProductUpdate(BaseSchema):
     CategoryID: Optional[int] = Field(None, gt=0)
     Name: Optional[str] = Field(None, min_length=1, max_length=50)
     Description: Optional[str] = Field(None, min_length=1, max_length=200)
     ImageUrl: Optional[str] = Field(None, min_length=1, max_length=255)

class ProductResponse(ProductBase):
     ProductID: int

     model_config = ConfigDict(from_attributes=True)

class ProductWithVariants(ProductResponse):
     variants: List["ProductVariantResponse"] = []

class ProductComplete(ProductResponse):
     categories: CategoryResponse
     product_variants: List["ProductVariantResponse"] = []

#======================================
# Sizes Schemas
#======================================
class SizeBase(BaseSchema):
    SizeName: str = Field(..., min_length=1, max_length=50)

class SizeCreate(SizeBase):
    pass

class SizeUpdate(BaseSchema):
    SizeName: Optional[str] = Field(None, min_length=1, max_length=50)

class SizeResponse(SizeBase):
    SizeID: int
    
    model_config = ConfigDict(from_attributes=True)

#======================================
# Types Schemas
#======================================
class TypeBase(BaseSchema):
    TypeName: str = Field(..., min_length=1, max_length=50)

class TypeCreate(TypeBase):
    pass

class TypeUpdate(BaseSchema):
    TypeName: Optional[str] = Field(None, min_length=1, max_length=50)

class TypeResponse(TypeBase):
    TypeID: int
    
    model_config = ConfigDict(from_attributes=True)

#======================================
# ProductVariant Schemas
#======================================
class ProductVariantBase(BaseSchema):
    ProductID: int = Field(..., gt=0)
    SizeID: int = Field(..., gt=0)
    TypeID: int = Field(..., gt=0)
    Price: Decimal = Field(..., gt=0)
    IsAvailable: bool = Field(default=True)

class ProductVariantCreate(ProductVariantBase):
    pass

class ProductVariantUpdate(BaseSchema):
    ProductID: Optional[int] = Field(None, gt=0)
    SizeID: Optional[int] = Field(None, gt=0)
    TypeID: Optional[int] = Field(None, gt=0)
    Price: Optional[Decimal] = Field(None, gt=0)
    IsAvailable: Optional[bool] = Field(default=True)

class ProductVariantResponse(ProductVariantBase):
    VariantID: int
    model_config = ConfigDict(from_attributes=True)


class ProductVariantComplete(ProductVariantResponse):
    """Product variant with all relationships"""
    products: ProductResponse
    sizes: SizeResponse
    types: TypeResponse
