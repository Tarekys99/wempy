#======================================
# invoice_api.py
#======================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import logging

from Database import db_connect
from Service.CreateDocx import extract_order_data, create_invoice_in_memory

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/invoices", tags=["Invoices"])

#=======================================
# 1. GET Generate Invoice DOCX
#=======================================

@router.get("/order/{order_id}")
def generate_invoice(
    order_id: int,
    db: Session = Depends(db_connect.get_db)
    ):
    """
    توليد فاتورة DOCX للطلب وتحميلها
    
    Args:
        order_id: رقم الطلب
    
    Returns:
        ملف DOCX للفاتورة
    """
    try:
        logger.info(f"بدء إنشاء فاتورة للطلب - OrderID: {order_id}")
        
        # استخراج بيانات الطلب
        invoice_data = extract_order_data(db, order_id)
        
        if not invoice_data:
            logger.error(f"الطلب غير موجود - OrderID: {order_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "الطلب غير موجود"}
            )
        
        # إنشاء الفاتورة في الذاكرة (بدون حفظ على القرص)
        file_stream, filename = create_invoice_in_memory(invoice_data)
        
        logger.info(f"تم إنشاء فاتورة للطلب {order_id}: {filename}")
        
        # إرجاع الملف مباشرة من الذاكرة
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
        logger.error(f"خطأ في إنشاء الفاتورة: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "حدث خطأ في إنشاء الفاتورة"}
        )