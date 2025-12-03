from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from Database.db_connect import get_db
from Database.models.product_model import Sizes, Types
from Database.pydantic_schema.product_schema import (
    SizeResponse,SizeUpdate,
    TypeResponse,TypeUpdate
)

size_router = APIRouter(prefix="/sizes", tags=["Sizes"])
type_router = APIRouter(prefix="/types", tags=["Types"])

# Sizes API
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
