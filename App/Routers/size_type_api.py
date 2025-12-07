from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from Database.db_connect import get_db
from Database.models.product_model import Sizes, Types
from Database.pydantic_schema.product_schema import (
    SizeCreate, SizeResponse, SizeUpdate,
    TypeCreate, TypeResponse, TypeUpdate
)

# إعداد Logger
logger = logging.getLogger("size_type_api")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(console_handler)

size_router = APIRouter(prefix="/sizes", tags=["Sizes"])
type_router = APIRouter(prefix="/types", tags=["Types"])

# Sizes API
@size_router.post("/add_size", response_model=SizeResponse, status_code=status.HTTP_201_CREATED)
def add_size(size: SizeCreate, db: Session = Depends(get_db)):
    logger.info(f"محاولة إضافة حجم جديد: '{size.SizeName}'")
    
    # التحقق من وجود الحجم
    existing = db.query(Sizes).filter(Sizes.SizeName == size.SizeName).first()
    if existing:
        logger.warning(f"الحجم '{size.SizeName}' موجود بالفعل - ID: {existing.SizeID}")
        raise HTTPException(status_code=400, detail=f"الحجم '{size.SizeName}' موجود بالفعل")
    
    try:
        new_size = Sizes(SizeName=size.SizeName)
        db.add(new_size)
        db.commit()
        db.refresh(new_size)
        logger.info(f"✓ تم إضافة الحجم بنجاح - ID: {new_size.SizeID}, Name: '{new_size.SizeName}'")
        return new_size
    except IntegrityError as e:
        db.rollback()
        logger.error(f"✗ خطأ IntegrityError: {str(e)}")
        raise HTTPException(status_code=400, detail=f"الحجم '{size.SizeName}' موجود بالفعل")
    except Exception as e:
        db.rollback()
        logger.error(f"✗ خطأ غير متوقع: {str(e)}")
        logger.error(f"نوع الخطأ: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"فشل إضافة الحجم: {str(e)}")

@size_router.get("/get_sizes", response_model=List[SizeResponse])
def get_all_sizes(db: Session = Depends(get_db)):
    return db.query(Sizes).order_by(Sizes.SizeID.asc()).all()

@size_router.put("/update_size/{size_name}", response_model=SizeResponse)
def update_size(
    size_name: str,
    size_update: SizeUpdate,
    db: Session = Depends(get_db),
):
    db_size = db.query(Sizes).filter(Sizes.SizeName == size_name).first()

    if db_size is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Size with name '{size_name}' not found",
        )

    update_data = size_update.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update",
        )

    try:
        if "SizeName" in update_data:
            db_size.SizeName = update_data["SizeName"]
        db.commit()
        db.refresh(db_size)
        return db_size

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Size with name '{size_update.SizeName}' already exists",
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update size",
        )

@size_router.delete("/delete_size/{size_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_size(size_name: str, db: Session = Depends(get_db)):

    db_size = db.query(Sizes).filter(Sizes.SizeName == size_name).first()

    if db_size is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Size with name '{size_name}' not found",
        )
    try:
        db.delete(db_size)
        db.commit()
        return None
        
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete size",
        )

# Types API
@type_router.post("/add_type", response_model=TypeResponse, status_code=status.HTTP_201_CREATED)
def add_type(type_data: TypeCreate, db: Session = Depends(get_db)):
    logger.info(f"محاولة إضافة نوع جديد: '{type_data.TypeName}'")
    
    # التحقق من وجود النوع
    existing = db.query(Types).filter(Types.TypeName == type_data.TypeName).first()
    if existing:
        logger.warning(f"النوع '{type_data.TypeName}' موجود بالفعل - ID: {existing.TypeID}")
        raise HTTPException(status_code=400, detail=f"النوع '{type_data.TypeName}' موجود بالفعل")
    
    try:
        new_type = Types(TypeName=type_data.TypeName)
        db.add(new_type)
        db.commit()
        db.refresh(new_type)
        logger.info(f"✓ تم إضافة النوع بنجاح - ID: {new_type.TypeID}, Name: '{new_type.TypeName}'")
        return new_type
    except IntegrityError as e:
        db.rollback()
        logger.error(f"✗ خطأ IntegrityError: {str(e)}")
        raise HTTPException(status_code=400, detail=f"النوع '{type_data.TypeName}' موجود بالفعل")
    except Exception as e:
        db.rollback()
        logger.error(f"✗ خطأ غير متوقع: {str(e)}")
        logger.error(f"نوع الخطأ: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"فشل إضافة النوع: {str(e)}")

@type_router.get("/get_types", response_model=List[TypeResponse])
def get_all_types(db: Session = Depends(get_db)):
    return db.query(Types).order_by(Types.TypeID.asc()).all()

@type_router.put("/update_type/{type_name}", response_model=TypeResponse)
def update_type(
    type_name: str,
    type_update: TypeUpdate,
    db: Session = Depends(get_db),
):
    db_type = db.query(Types).filter(Types.TypeName == type_name).first()

    if db_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Type with name '{type_name}' not found",
        )

    update_data = type_update.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update",
        )

    try:
        if "TypeName" in update_data:
            db_type.TypeName = update_data["TypeName"]

        db.commit()
        db.refresh(db_type)
        return db_type

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type with name '{type_update.TypeName}' already exists",
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update type",
        )


@type_router.delete("/delete_type/{type_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_type(type_name: str, db: Session = Depends(get_db)):
    db_type = db.query(Types).filter(Types.TypeName == type_name).first()

    if db_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Type with name '{type_name}' not found",
        )
    try:
        db.delete(db_type)
        db.commit()
        return None
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete type",
        )
