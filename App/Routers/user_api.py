from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import uuid

from Database.pydantic_schema import user_schema
from Database.models.user_model import User
from Database import db_connect
from config import response

router = APIRouter(
     prefix="/users",
     tags=["Users"]
)

"""
- مجلد ال router يحتوي على جميع APIs endpoints 
     -> ثم تشغيلها من الملف الرئيسي
"""

@router.get("/all_users", response_model=list[user_schema.UserResponse])
def get_all_users(db: Session = Depends(db_connect.get_db)):
     users = db.query(User).all()
     return users

@router.post("/register", response_model=user_schema.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: user_schema.UserCreate,
                  db: Session=Depends(db_connect.get_db)):
     
     try:
          # التحقق من وجود المستخدم
          existing_user = db.query(User).filter(User.PhoneNumber == user.PhoneNumber).first()
          if existing_user:
               raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                         "error": response.USER_ALREADY_EXISTS,
                         "phone_number": user.PhoneNumber
                    }
               )

          # إنشاء مستخدم جديد
          user_data = user.model_dump()
          user_data['UserID'] = str(uuid.uuid4())  # توليد UUID
          new_user = User(**user_data)
          
          db.add(new_user)
          db.commit()
          db.refresh(new_user)
          
          return new_user
          
     except HTTPException:
          raise
     except SQLAlchemyError as e:
          db.rollback()
          raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail={
                    "error": response.DATABASE_ERROR,
                    "message": "فشل حفظ البيانات"
               }
          )
     except Exception as e:
          db.rollback()
          raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail={
                    "error": response.INTERNAL_ERROR,
                    "message": str(e)}
          )


@router.post("/login", response_model=user_schema.UserResponse)
def login_user(data: user_schema.UserLogin, db: Session = Depends(db_connect.get_db)):

    try:
        # البحث عن المستخدم
        user = db.query(User).filter(User.PhoneNumber == data.PhoneNumber).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": response.USER_NOT_FOUND}
            )
        
        # تحديث تاريخ آخر تسجيل دخول
        user.lastLogin = datetime.now()
        db.commit()
        db.refresh(user)
        
        return user
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": response.DATABASE_ERROR}
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": response.INTERNAL_ERROR}
        )


@router.put("/update/{user_id}", response_model=user_schema.UserResponse)
def update_user(user_id: str, 
                user_update: user_schema.UserUpdate,
                db: Session = Depends(db_connect.get_db)):
    try:
        # البحث عن المستخدم
        user = db.query(User).filter(User.UserID == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": response.USER_NOT_FOUND}
            )
        
        # التحقق من وجود بيانات للتحديث
        update_data = user_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": response.NO_CHANGES_MADE,
                    "message": "يجب إرسال حقل واحد على الأقل للتحديث"
                }
            )
        
        # التحقق من عدم تكرار رقم الهاتف إذا تم تحديثه
        if "PhoneNumber" in update_data:
            existing_phone = db.query(User).filter(
                User.PhoneNumber == update_data["PhoneNumber"],
                User.UserID != user_id
            ).first()
            
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": response.USER_ALREADY_EXISTS}
                )
        
        # تحديث البيانات
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return user
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": response.DATABASE_ERROR,
                "message": "فشل تحديث البيانات"
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": response.INTERNAL_ERROR,
                "message": str(e)
            }
        )