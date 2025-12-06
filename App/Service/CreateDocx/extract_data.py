from sqlalchemy.orm import Session, joinedload
from Database.models.orders_info_model import Order
from Database.models.order_item_model import OrderItem
from Database.models.product_model import ProductVariant
from Database.models.address_zone_model import Address
from typing import Dict, Any
from decimal import Decimal


def extract_order_data(db: Session, order_id: int) -> Dict[str, Any]:
    """
    استخراج كل بيانات الطلب المطلوبة للفاتورة
    
    Args:
        db: Database session
        order_id: رقم الطلب
    
    Returns:
        Dict يحتوي على كل بيانات الفاتورة
    """
    
    # جلب الطلب مع كل العلاقات
    order = db.query(Order).options(
        joinedload(Order.order_items).joinedload(OrderItem.product_variants).joinedload(ProductVariant.products),
        joinedload(Order.order_items).joinedload(OrderItem.product_variants).joinedload(ProductVariant.sizes),
        joinedload(Order.order_items).joinedload(OrderItem.product_variants).joinedload(ProductVariant.types),
        joinedload(Order.address).joinedload(Address.delivery_zone),
        joinedload(Order.payment_method),
        joinedload(Order.shifts)
    ).filter(Order.OrderID == order_id).first()
    
    if not order:
        return None
    
    # استخراج البيانات الأساسية
    invoice_data = {
        # معلومات الطلب
        "order_number": order.OrderNumber,
        "order_date": order.OrderTimestamp.strftime("%Y-%m-%d %H:%M"),
        "order_status": order.OrderStatus.value,
        
        # معلومات الشفت
        "shift_number": order.shifts.Shift_Number,
        "shift_date": order.shifts.Shift_Date.strftime("%Y-%m-%d"),
        
        # معلومات المستلم (من العنوان)
        "recipient_name": order.address.RecipientName,
        "recipient_phone": order.address.RecipientPhone,
        "recipient_phone2": order.address.Phone2 if order.address.Phone2 else "",
        
        # العنوان
        "city": order.address.City,
        "street": order.address.Street,
        "building": order.address.Building,
        "delivery_notes": order.address.DeliveryNotes,
        
        # معلومات المنطقة
        "zone_name": order.address.delivery_zone.ZoneName,
        "zone_delivery_cost": float(order.address.delivery_zone.DeliveryCost),
        
        # طريقة الدفع
        "payment_method": order.payment_method.PaymentName,
        "payment_id": order.payment_method.PaymentID,
        
        # ملاحظات الطلب
        "order_notes": order.OrderNotes if order.OrderNotes else "لا توجد ملاحظات",
        "external_notes": order.ExternalNotes if order.ExternalNotes else "",
        
        # التكاليف
        "delivery_fee": float(order.DeliveryFee),
        "total_price": float(order.TotalPrice),
        
        # المنتجات
        "items": []
    }
    
    # استخراج تفاصيل المنتجات
    items_subtotal = Decimal('0.00')
    
    for order_item in order.order_items:
        variant = order_item.product_variants
        
        # تحديد المتغير (حجم أو نوع) مع التحقق من None
        size_name = variant.sizes.SizeName if hasattr(variant, 'sizes') and variant.sizes else ""
        type_name = variant.types.TypeName if hasattr(variant, 'types') and variant.types else ""
        
        # فلترة "افتراضي" - لا نعرضه في الفاتورة
        if size_name and size_name.lower() == "افتراضي":
            size_name = ""
        if type_name and type_name.lower() == "افتراضي":
            type_name = ""
        
        # دمج الحجم والنوع (فقط إذا كانا غير فارغين)
        if size_name and type_name:
            variant_info = f"{size_name} - {type_name}"
        elif size_name:
            variant_info = size_name
        elif type_name:
            variant_info = type_name
        else:
            variant_info = ""  # لا يوجد متغير للعرض
        
        item_data = {
            "product_name": variant.products.Name,
            "variant_info": variant_info,
            "unit_price": float(order_item.UnitPrice),
            "quantity": order_item.Quantity,
            "subtotal": float(order_item.Subtotal)
        }
        
        invoice_data["items"].append(item_data)
        items_subtotal += order_item.Subtotal
    
    # إضافة مجموع المنتجات
    invoice_data["items_subtotal"] = float(items_subtotal)
    
    return invoice_data