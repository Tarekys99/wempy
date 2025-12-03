from pydantic import BaseModel, ConfigDict
from datetime import date, time
from typing import List, Optional

#======================================
# Shift Report Schemas
#======================================

class ShiftBasicInfo(BaseModel):
    """معلومات الشفت الأساسية"""
    shift_number: str
    shift_date: date
    start_time: time
    end_time: Optional[time]
    duration_hours: float  # مدة الشفت بالساعات
    
    model_config = ConfigDict(from_attributes=True)


class OrdersStatistics(BaseModel):
    """إحصائيات الطلبات"""
    total_orders: int
    delivered_orders: int
    cancelled_orders: int
    
    model_config = ConfigDict(from_attributes=True)


class FinancialStatistics(BaseModel):
    """الإحصائيات المالية"""
    total_sales: float  # إجمالي المبيعات
    total_delivery_fees: float  # إجمالي رسوم التوصيل
    products_value: float  # قيمة المنتجات فقط
    average_order_value: float  # متوسط قيمة الطلب
    
    model_config = ConfigDict(from_attributes=True)


class PaymentMethodBreakdown(BaseModel):
    """توزيع طريقة دفع واحدة"""
    payment_method: str
    orders_count: int
    total_amount: float
    percentage: float
    
    model_config = ConfigDict(from_attributes=True)


class ShiftReportResponse(BaseModel):
    """الاستجابة الكاملة لتقرير الشفت"""
    shift_info: ShiftBasicInfo
    orders_stats: OrdersStatistics
    financial_stats: FinancialStatistics
    payment_methods: List[PaymentMethodBreakdown]
    
    model_config = ConfigDict(from_attributes=True)
