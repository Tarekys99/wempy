from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime, date
import logging

from Database.db_connect import get_db
from Database.models.shift_model import Shift
from Database.pydantic_schema.shift_schema import ShiftStart, ShiftResponse
from Database.pydantic_schema.shift_report_schema import ShiftReportResponse
from Service.ShiftReport.shift_report_service import get_shift_report_data
from Service.CreateDocx.shift_report_docx import create_shift_report_in_memory

logger = logging.getLogger("shifts")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)

#======================================
# Shifts API 
#======================================
router = APIRouter(prefix="/shifts", tags=["Shifts"])

@router.post("/start_shift", response_model=ShiftResponse, status_code=201)
def start_shift(data: ShiftStart,
                 db: Session = Depends(get_db)):
    
    today = date.today()
    now = datetime.now().time()
    
    # التحقق: هل الوردية مفتوحة اليوم؟
    existing = db.query(Shift).filter(
        Shift.Shift_Date == today,
        Shift.Shift_Number == data.Shift_Number,
        Shift.End_Time == None
    ).first()
    
    if existing:
        raise HTTPException(400, f"وردية {data.Shift_Number} مفتوحة بالفعل")
    
    try:
        shift = Shift(
            Shift_Date=today,
            Shift_Number=data.Shift_Number,
            Start_Time=now,
            End_Time=None,
            IsActive=True
        )
        db.add(shift)
        db.commit()
        db.refresh(shift)
        
        logger.info(f"✓ بدء وردية {shift.Shift_Number}")
        return shift
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "الوردية موجودة بالفعل")
    except Exception as e:
        db.rollback()
        logger.error(f"✗ خطأ: {e}")
        raise HTTPException(500, "فشل بدء الوردية")


# إنهاء  shift_id
@router.patch("/end_shift/{shift_id}")
def end_shift(shift_id: int, db: Session = Depends(get_db)):
    
    # البحث بـ ShiftID
    shift = db.query(Shift).filter(
        Shift.ShiftID == shift_id,
        Shift.End_Time == None  # مفتوحة
    ).first()
    
    if not shift:
        raise HTTPException(404, f"لا توجد وردية بهذا الرقم أو أنها منتهية بالفعل")
    
    try:
        shift.End_Time = datetime.now().time()
        shift.IsActive = False
        db.commit()
        db.refresh(shift)
        
        logger.info(f"✓ إنهاء وردية {shift.Shift_Number}")
        return shift
    except Exception as e:
        db.rollback()
        raise HTTPException(500, "فشل إنهاء الوردية")


@router.patch("/toggle_active/{shift_id}", response_model=ShiftResponse)
def toggle_active(shift_id: int, db: Session = Depends(get_db)):
    """إيقاف/استئناف الوردية"""
    
    shift = db.query(Shift).filter(Shift.ShiftID == shift_id).first()
    
    if not shift:
        raise HTTPException(404, "الوردية غير موجودة")
    
    if shift.End_Time:
        raise HTTPException(400, "الوردية منتهية")
    
    try:
        shift.IsActive = not shift.IsActive
        db.commit()
        db.refresh(shift)
        
        status = "نشطة" if shift.IsActive else "متوقفة"
        logger.info(f"✓ تغيير حالة وردية {shift.Shift_Number} إلى {status}")
        return shift
        
    except Exception as e:
        db.rollback()
        logger.error(f"✗ خطأ: {e}")
        raise HTTPException(500, "فشل تغيير الحالة")

@router.get("/all_shifts", response_model=List[ShiftResponse])
def get_all_shifts(db: Session = Depends(get_db)):
    """جلب كل الشفتات"""
    
    shifts = db.query(Shift).order_by(
        Shift.Shift_Date.desc(),
        Shift.Start_Time.desc()
    ).all()
    
    logger.info(f"✓ عرض {len(shifts)} وردية")
    return shifts


@router.get("/shifts_by_date/{shift_date}", response_model=List[ShiftResponse])
def get_shifts_by_date(shift_date: date, db: Session = Depends(get_db)):
    """عرض ورديات يوم محدد"""
    
    shifts = db.query(Shift).filter(
        Shift.Shift_Date == shift_date
    ).order_by(Shift.Start_Time).all()
    
    logger.info(f"✓ عرض {len(shifts)} وردية بتاريخ {shift_date}")
    return shifts


#======================================
# Shift Report API - تقرير تقفيل الشفت
#======================================

@router.get("/report/{shift_id}", response_model=ShiftReportResponse)
def get_shift_report(shift_id: int, db: Session = Depends(get_db)):
    """
    جلب تقرير الشفت كـ JSON
    
    Args:
        shift_id: رقم الشفت (ShiftID)
    
    Returns:
        تقرير شامل عن الشفت
    """
    try:
        report_data = get_shift_report_data(db, shift_id)
        
        if not report_data:
            raise HTTPException(404, "الشفت غير موجود")
        
        logger.info(f"✓ تم جلب تقرير الشفت {shift_id}")
        return report_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ خطأ في جلب تقرير الشفت: {e}")
        raise HTTPException(500, "فشل جلب تقرير الشفت")


@router.get("/report/{shift_id}/download")
def download_shift_report(shift_id: int, db: Session = Depends(get_db)):

    try:
        # 1. جلب بيانات التقرير
        report_data = get_shift_report_data(db, shift_id)
        
        if not report_data:
            raise HTTPException(404, "الشفت غير موجود")
        
        # 2. إنشاء ملف DOCX
        file_stream, filename = create_shift_report_in_memory(report_data)
        
        logger.info(f"✓ تم إنشاء تقرير DOCX للشفت {shift_id}")
        
        # 3. إرجاع الملف للتحميل
        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ خطأ في تحميل تقرير الشفت: {e}")
        raise HTTPException(500, f"فشل تحميل تقرير الشفت: {str(e)}")