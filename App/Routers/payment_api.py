from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List

from Database.db_connect import get_db
from Database.models.payment_model import PaymentMethod # الجدول نفسه
from Database.pydantic_schema.payment_schema import (
    PaymentCreate,
    PaymentResponse
)

payment_router = APIRouter(prefix="/payment", tags=["Payment"])

# ======================================
# Payment API
# ======================================

# Get All Payment Methods
@payment_router.get("/all_payment_methods", response_model=List[PaymentResponse])
def list_payment_methods(db: Session = Depends(get_db)):
    return db.query(PaymentMethod).order_by(PaymentMethod.PaymentID.asc()).all()

# Create Payment Method
@payment_router.post("/create_payment_method", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment_method(
     payment_in: PaymentCreate,
     db: Session = Depends(get_db)):
    try:
        payment = PaymentMethod(**payment_in.model_dump())
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="طريقة الدفع موجودة بالفعل"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="فشل إضافة طريقة دفع جديدة"
        )

# Delete Payment Method
@payment_router.delete("/delete_payment_method/{payment_id}")
def delete_payment_method(
    payment_id: int,
    db: Session = Depends(get_db)
):
    payment = db.query(PaymentMethod).filter(PaymentMethod.PaymentID == payment_id).first()
    
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="طريقة الدفع غير موجودة"
        )
    try:
        db.delete(payment)
        db.commit()
        return {"message": "تم الحذف"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="فشل الحذف"
        )
