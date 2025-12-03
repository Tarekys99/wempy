from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, Any

from Database.models.shift_model import Shift
from Database.models.orders_info_model import Order, OrderStatus
from Database.models.payment_model import PaymentMethod
from Database.pydantic_schema.shift_report_schema import (
    ShiftBasicInfo,
    OrdersStatistics,
    FinancialStatistics,
    PaymentMethodBreakdown,
    ShiftReportResponse
)


def calculate_duration_hours(start_time, end_time) -> float:
    """حساب مدة الشفت بالساعات"""
    if not end_time:
        # إذا كان الشفت مفتوح، نستخدم الوقت الحالي
        end_time = datetime.now().time()
    
    # تحويل time إلى datetime للحساب
    today = datetime.today().date()
    start_dt = datetime.combine(today, start_time)
    end_dt = datetime.combine(today, end_time)
    
    # إذا كان وقت النهاية أقل من البداية، معناها اليوم التالي
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    
    duration = end_dt - start_dt
    return round(duration.total_seconds() / 3600, 2)  # تحويل إلى ساعات


def get_shift_report_data(db: Session, shift_id: int) -> Dict[str, Any]:
    """
    جلب كل بيانات تقرير الشفت
    
    Args:
        db: Database session
        shift_id: رقم الشفت
    
    Returns:
        Dict يحتوي على كل بيانات التقرير
    """
    
    # 1. جلب الشفت
    shift = db.query(Shift).filter(Shift.ShiftID == shift_id).first()
    
    if not shift:
        return None
    
    # 2. جلب كل الطلبات المرتبطة بالشفت
    orders = db.query(Order).filter(Order.ShiftID == shift_id).all()
    
    # 3. حساب معلومات الشفت الأساسية
    duration_hours = calculate_duration_hours(shift.Start_Time, shift.End_Time)
    
    shift_info = ShiftBasicInfo(
        shift_number=shift.Shift_Number,
        shift_date=shift.Shift_Date,
        start_time=shift.Start_Time,
        end_time=shift.End_Time,
        duration_hours=duration_hours
    )
    
    # 4. حساب إحصائيات الطلبات
    total_orders = len(orders)
    delivered_orders = len([o for o in orders if o.OrderStatus == OrderStatus.DELIVERED])
    cancelled_orders = len([o for o in orders if o.OrderStatus == OrderStatus.CANCELLED])
    
    orders_stats = OrdersStatistics(
        total_orders=total_orders,
        delivered_orders=delivered_orders,
        cancelled_orders=cancelled_orders
    )
    
    # 5. حساب الإحصائيات المالية
    total_sales = sum(float(o.TotalPrice) for o in orders)
    total_delivery_fees = sum(float(o.DeliveryFee) for o in orders)
    products_value = total_sales - total_delivery_fees
    average_order_value = total_sales / total_orders if total_orders > 0 else 0.0
    
    financial_stats = FinancialStatistics(
        total_sales=round(total_sales, 2),
        total_delivery_fees=round(total_delivery_fees, 2),
        products_value=round(products_value, 2),
        average_order_value=round(average_order_value, 2)
    )
    
    # 6. حساب توزيع طرق الدفع
    payment_breakdown = []
    
    # استعلام لجمع البيانات حسب طريقة الدفع
    payment_stats = db.query(
        PaymentMethod.PaymentName,
        func.count(Order.OrderID).label('count'),
        func.sum(Order.TotalPrice).label('total')
    ).join(Order, Order.PaymentID == PaymentMethod.PaymentID)\
     .filter(Order.ShiftID == shift_id)\
     .group_by(PaymentMethod.PaymentName)\
     .all()
    
    for method_name, count, total in payment_stats:
        percentage = (float(total) / total_sales * 100) if total_sales > 0 else 0.0
        
        payment_breakdown.append(PaymentMethodBreakdown(
            payment_method=method_name,
            orders_count=count,
            total_amount=round(float(total), 2),
            percentage=round(percentage, 2)
        ))
    
    # 7. إنشاء الاستجابة الكاملة
    report_data = {
        "shift_info": shift_info.model_dump(),
        "orders_stats": orders_stats.model_dump(),
        "financial_stats": financial_stats.model_dump(),
        "payment_methods": [pm.model_dump() for pm in payment_breakdown]
    }
    
    return report_data
