from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List

from Database.db_connect import get_db
from Database.models.product_model import Products, ProductVariant, Sizes, Types
from Database.pydantic_schema.product_schema import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ProductVariantComplete,
    ProductVariantCreate,
    ProductVariantUpdate
)

products_router = APIRouter(prefix="/products", tags=["Products"])
variants_router = APIRouter(prefix="/product_variants", tags=["Product Variants"])

# ======================================
# Products API
# ======================================

# Get All Products, not complete product
@products_router.get("/all_products", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return db.query(Products).order_by(Products.ProductID.asc()).all()

# Create Product
@products_router.post("/create_product", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
     product_in: ProductCreate,
     db: Session = Depends(get_db)):

    product = Products(**product_in.model_dump())
    try:
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category reference or product already exists",
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product")

# Update Product
@products_router.put("/update_product/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)):

    # 1st search product by id
    product = db.query(Products).filter(Products.ProductID == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id '{product_id}' not found")

    # 2nd update product
    update_data = product_update.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update")

    try:
        if "CategoryID" in update_data:
            product.CategoryID = update_data["CategoryID"]
        if "Name" in update_data:
            product.Name = update_data["Name"]
        if "Description" in update_data:
            product.Description = update_data["Description"]
        if "ImageUrl" in update_data:
            product.ImageUrl = update_data["ImageUrl"]

        db.commit()
        db.refresh(product)
        return product
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update product due to constraint violation",
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product",
        )

# Delete Product
@products_router.delete("/delete_product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
     product_id: int,
     db: Session = Depends(get_db)):
    
    # 1st search product by id
    product = db.query(Products).filter(Products.ProductID == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id '{product_id}' not found")

    # 2nd delete product
    try:
        db.delete(product)
        db.commit()
        return None
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product",
        )

# ======================================
# ProductVariant API
# ======================================

# Get All Products
@variants_router.get("/all_products", response_model=List[ProductVariantComplete])
def list_all_products(db: Session = Depends(get_db)):
    return db.query(ProductVariant).order_by(ProductVariant.VariantID.asc()).all()

# Create Product Variant
@variants_router.post("/create_variant", response_model=ProductVariantComplete, status_code=status.HTTP_201_CREATED)
def create_product_variant(
    variant_in: ProductVariantCreate,
    db: Session = Depends(get_db)):
    """
    - check if the product, size, and type exist
       -> put values of FKs 
    - and create a new Price and Availability
    """
    if db.query(Products).filter(Products.ProductID == variant_in.ProductID).first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id '{variant_in.ProductID}' not found",
        )

    if db.query(Sizes).filter(Sizes.SizeID == variant_in.SizeID).first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Size with id '{variant_in.SizeID}' not found",
        )

    if db.query(Types).filter(Types.TypeID == variant_in.TypeID).first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Type with id '{variant_in.TypeID}' not found",
        )

    variant = ProductVariant(**variant_in.model_dump())

    try:
        db.add(variant)
        db.commit()
        db.refresh(variant)
        return variant

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product variant with the same attributes already exists",
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product variant",
        )

# Get Product Variant
@variants_router.get("/get_variant/{variant_id}", response_model=ProductVariantComplete)
def get_product_variant(
    variant_id: int,
    db: Session = Depends(get_db),
):
    variant = db.query(ProductVariant).filter(ProductVariant.VariantID == variant_id).first()
    if variant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ProductVariant with id '{variant_id}' not found",
        )
    return variant

# Update Product Variant
@variants_router.put("/update_variant/{variant_id}", response_model=ProductVariantComplete)
def update_product_variant(
    variant_id: int,
    variant_update: ProductVariantUpdate,
    db: Session = Depends(get_db)):

    variant = db.query(ProductVariant).filter(ProductVariant.VariantID == variant_id).first()
    if variant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ProductVariant with id '{variant_id}' not found",
        )

    update_data = variant_update.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update",
        )
     # check if the ProductID, SizeID, TypeID exist in original tables
    if "ProductID" in update_data and db.query(Products).filter(Products.ProductID == update_data["ProductID"]).first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id '{update_data['ProductID']}' not found")

    if "SizeID" in update_data and db.query(Sizes).filter(Sizes.SizeID == update_data["SizeID"]).first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Size with id '{update_data['SizeID']}' not found")

    if "TypeID" in update_data and db.query(Types).filter(Types.TypeID == update_data["TypeID"]).first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Type with id '{update_data['TypeID']}' not found")

    try:
        if "ProductID" in update_data:
            variant.ProductID = update_data["ProductID"]
        if "SizeID" in update_data:
            variant.SizeID = update_data["SizeID"]
        if "TypeID" in update_data:
            variant.TypeID = update_data["TypeID"]
        if "Price" in update_data:
            variant.Price = update_data["Price"]
        if "IsAvailable" in update_data:
            variant.IsAvailable = update_data["IsAvailable"]

        db.commit()
        db.refresh(variant)
        return variant
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update product variant due to constraint violation",
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product variant",
        )

@variants_router.delete("/delete_variant/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_variant(
    variant_id: int,
    db: Session = Depends(get_db)):

    variant = db.query(ProductVariant).filter(ProductVariant.VariantID == variant_id).first()
    if variant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ProductVariant with id '{variant_id}' not found",
        )
    try:
        db.delete(variant)
        db.commit()
        return None
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product variant",
        )

