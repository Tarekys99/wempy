from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import IntegrityError

from Database.db_connect import get_db
from Database.models.product_model import Category # db class
from Database.pydantic_schema.product_schema import(
     CategoryCreate,
     CategoryResponse,
     CategoryWithProducts,
     CategoryUpdate
     )

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/get_all_categories", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):

    categories = db.query(Category).order_by(Category.CategoryID.asc()).all()
    return categories

@router.post("/create_category", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate,
                    db: Session = Depends(get_db)):
    """
    - بعد انشاء كلاس جدول البيانات
    - يتم انشاء كائن منه ليقوم بكل العمليات
    """
    try:
        # create object from db class
        # لو اسم الفئة من الكلاس مطابق لتحقق بايدانتك يبقا اضف البيانات
        db_category = Category(
            CategoryName=category.CategoryName) # passing ClassName from pydantic_schema to db model
            
        # add to database
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category.CategoryName}' already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create category"
        )
@router.get("/get_category_with_products/{category_name}", response_model=CategoryWithProducts)
def get_category_with_products(
    category_name: str,
    db: Session = Depends(get_db)):

    # search for category_name
    db_category = db.query(Category).filter(Category.CategoryName == category_name).first()
    
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category: '{category_name}' not found"
        )
    return db_category

@router.put("/update_category/{category_name}", response_model=CategoryResponse)
def update_category(
    category_name: str,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db)):
    
    db_category = db.query(Category).filter(Category.CategoryName == category_name).first()
    
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category: '{category_name}' not found"
        )
    
    try:
        if category_update.CategoryName is not None:
            db_category.CategoryName = category_update.CategoryName
        
        db.commit()
        db.refresh(db_category)
        return db_category
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category_update.CategoryName}' already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update category"
        )

@router.delete("/delete_category/{category_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_name: str,
    db: Session = Depends(get_db)
    ):

    db_category = db.query(Category).filter(Category.CategoryName == category_name).first()
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category: '{category_name}' not found")
    
    try:
        db.delete(db_category)
        db.commit()
        return None
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category")