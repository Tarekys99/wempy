#======================================
# order_api.py
#======================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from decimal import Decimal
import logging
from typing import List

from Database.pydantic_schema import orders_schema
from Database.models.orders_info_model import Order, OrderStatus

from Database.models.order_item_model import OrderItem
from Database.models.product_model import ProductVariant
from Database.models.address_zone_model import Address
from Database.models.user_model import User
from Database import db_connect

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["Orders"])

#===========================
# 1.POST Create Order
#===========================

@router.post("/create", response_model=orders_schema.OrderListResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: orders_schema.OrderCreate,
    db: Session = Depends(db_connect.get_db)):
    try:
        logger.info(f"بدء إنشاء طلب - UserID: {order_data.UserID}")
        
        # التحقق من المستخدم
        user = db.query(User).filter(User.UserID == order_data.UserID).first()
        if not user:
            logger.error(f"المستخدم غير موجود - UserID: {order_data.UserID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "المستخدم غير موجود"}
            )
        
        # التحقق من العنوان وجلب تكلفة التوصيل
        address = db.query(Address).options(
            joinedload(Address.delivery_zone)
        ).filter(
            Address.AddressID == order_data.AddressID,
            Address.UserID == order_data.UserID
        ).first()
        
        if not address:
            logger.error(f"العنوان غير موجود - AddressID: {order_data.AddressID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "العنوان غير موجود أو لا يخص هذا المستخدم"})
        
        delivery_cost = address.delivery_zone.DeliveryCost
        logger.info(f"العنوان: {address.City} - تكلفة التوصيل: {delivery_cost}")
        
        # التحقق من المنتجات وحساب المجموع
        order_items_data = []
        items_total = Decimal('0.00')
        
        for item in order_data.items:
            variant = db.query(ProductVariant).filter(
                ProductVariant.VariantID == item.VariantID
            ).first()
            
            if not variant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": f"المنتج رقم {item.VariantID} غير موجود"})
            
            if not variant.IsAvailable:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"error": f"المنتج رقم {item.VariantID} غير متوفر حالياً"})
            
            unit_price = Decimal(str(variant.Price))
            subtotal = unit_price * item.Quantity
            items_total += subtotal
            
            order_items_data.append({
                'variant': variant,
                'quantity': item.Quantity,
                'unit_price': unit_price,
                'subtotal': subtotal
            })
        
        total_price = items_total + delivery_cost
        logger.info(f"السعر الإجمالي: {total_price}")
        
        # حساب OrderNumber بناءً على الشفت الحالي
        last_order = db.query(Order).filter(
            Order.ShiftID == order_data.ShiftID
        ).order_by(Order.OrderNumber.desc()).first()
        order_number = (last_order.OrderNumber + 1) if last_order else 1
        
        # إنشاء الطلب
        new_order = Order(
            UserID=order_data.UserID,
            AddressID=order_data.AddressID,
            PaymentID=order_data.PaymentID,
            ShiftID=order_data.ShiftID,
            OrderNumber=order_number,
            DeliveryFee=delivery_cost,
            TotalPrice=total_price,
            OrderNotes=order_data.OrderNotes,
            ExternalNotes=order_data.ExternalNotes
        )
        
        db.add(new_order)
        db.flush()
        
        # إنشاء عناصر الطلب
        for item_data in order_items_data:
            order_item = OrderItem(
                OrderID=new_order.OrderID,
                VariantID=item_data['variant'].VariantID,
                Quantity=item_data['quantity'],
                UnitPrice=item_data['unit_price'],
                Subtotal=item_data['subtotal']
            )
            db.add(order_item)
        
        db.commit()
        db.refresh(new_order)
        
        logger.info(f"تم إنشاء الطلب - OrderID: {new_order.OrderID}")
        return new_order
        
    except HTTPException:
        db.rollback()
        raise
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"خطأ IntegrityError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "خطأ في البيانات المدخلة"})
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"خطأ SQLAlchemyError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "حدث خطأ في النظام"})
        
    except Exception as e:
        db.rollback()
        logger.error(f"خطأ غير متوقع: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "حدث خطأ غير متوقع"})

#===========================
# 2.GET All Orders
#===========================

@router.get("/all", response_model=List[orders_schema.OrderListResponse])
def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(db_connect.get_db)
    ):

    try:
        if limit > 500:
            limit = 500
        
        orders = db.query(Order).order_by(
            Order.OrderTimestamp.desc()
        ).offset(skip).limit(limit).all()
        
        logger.info(f"تم جلب {len(orders)} طلب")
        return orders
        
    except SQLAlchemyError as e:
        logger.error(f"خطأ في قاعدة البيانات: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "فشل جلب الطلبات"})
        
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "حدث خطأ غير متوقع"})

#=====================================
# 3.GET Order by userID 
#=====================================

@router.get("/user_orders/{user_id}", response_model=List[orders_schema.OrderListResponse])
def get_user_orders(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(db_connect.get_db)
    ):
    """جلب طلبات مستخدم معين"""
    try:
        if limit > 500:
            limit = 500
        
        # التحقق من وجود المستخدم
        user = db.query(User).filter(User.UserID == user_id).first()
        if not user:
            logger.error(f"المستخدم غير موجود - UserID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "المستخدم غير موجود"})
        
        orders = db.query(Order).filter(
            Order.UserID == user_id
        ).order_by(
            Order.OrderTimestamp.desc()
        ).offset(skip).limit(limit).all()
        
        logger.info(f"تم جلب {len(orders)} طلب للمستخدم {user_id}")
        return orders
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"خطأ في قاعدة البيانات: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "فشل جلب الطلبات"})
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "حدث خطأ غير متوقع"})


#=====================================
# 4. GET Order Details
#=====================================

@router.get("/order_details/{order_id}", response_model=orders_schema.OrderResponse)
def get_order_details(
    order_id: int,
    db: Session = Depends(db_connect.get_db)
    ):
    """جلب تفاصيل طلب معين باستخدام OrderID فقط"""
    try:
        order = db.query(Order).options(
            joinedload(Order.order_items).joinedload(OrderItem.product_variants).joinedload(ProductVariant.products),
            joinedload(Order.order_items).joinedload(OrderItem.product_variants).joinedload(ProductVariant.sizes),
            joinedload(Order.order_items).joinedload(OrderItem.product_variants).joinedload(ProductVariant.types)
        ).filter(
            Order.OrderID == order_id
        ).first()
        
        if not order:
            logger.error(f"الطلب غير موجود - OrderID: {order_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "الطلب غير موجود"})
        
        logger.info(f"تم جلب تفاصيل الطلب {order_id}")
        return order
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"خطأ في قاعدة البيانات: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "فشل جلب تفاصيل الطلب"})
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "حدث خطأ غير متوقع"})

#=====================================
# 5. GET User Active Orders (Secured)
#=====================================

@router.get("/user/{user_id}/active", response_model=List[orders_schema.OrderListResponse])
def get_user_active_orders(
    user_id: str,
    db: Session = Depends(db_connect.get_db)
    ):
    """جلب الطلبات النشطة لمستخدم معين"""
    try:
        # التحقق من وجود المستخدم
        user = db.query(User).filter(User.UserID == user_id).first()
        if not user:
            logger.error(f"المستخدم غير موجود - UserID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "المستخدم غير موجود"})
        
        orders = db.query(Order).filter(
            Order.UserID == user_id,
            Order.OrderStatus.in_([
                OrderStatus.PREPARING,
                OrderStatus.IN_DELIVERY
            ])
        ).order_by(
            Order.OrderTimestamp.desc()
        ).all()
        
        logger.info(f"تم جلب {len(orders)} طلب نشط للمستخدم {user_id}")
        return orders
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"خطأ في قاعدة البيانات: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "فشل جلب الطلبات النشطة"})
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "حدث خطأ غير متوقع"})

#===============================
# 6. PATCH Cancel Order (Secured)
#===============================

@router.patch("/user/{user_id}/cancel/{order_id}", response_model=orders_schema.OrderListResponse)
def cancel_user_order(
    user_id: str,
    order_id: int,
    db: Session = Depends(db_connect.get_db)
    ):
    """
    إلغاء طلب (مع التحقق من المستخدم)
    """
    try:
        # جلب الطلب مع التحقق المباشر
        order = db.query(Order).filter(
            Order.OrderID == order_id,
            Order.UserID == user_id  # ✅ تحقق مباشر
        ).first()
        
        if not order:
            logger.error(f"الطلب غير موجود أو لا يخص المستخدم - OrderID: {order_id}, UserID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "الطلب غير موجود أو لا يخصك"})
        
        if order.OrderStatus == OrderStatus.CANCELLED:
            logger.warning(f"الطلب ملغى مسبقاً - OrderID: {order_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "الطلب ملغى مسبقاً"})
        
        if order.OrderStatus == OrderStatus.DELIVERED:
            logger.warning(f"لا يمكن إلغاء طلب مكتمل - OrderID: {order_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "لا يمكن إلغاء طلب تم توصيله"})
        
        order.OrderStatus = OrderStatus.CANCELLED
        db.commit()
        db.refresh(order)
        
        logger.info(f"تم إلغاء الطلب {order_id} بواسطة المستخدم {user_id}")
        return order
        
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"خطأ في قاعدة البيانات: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "فشل إلغاء الطلب"})
    except Exception as e:
        db.rollback()
        logger.error(f"خطأ غير متوقع: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "حدث خطأ غير متوقع"})

#===============================
# 7.GET Orders by Status (Secured)
#===============================

@router.get("/user/{user_id}/status/{order_status}", response_model=List[orders_schema.OrderListResponse])
def get_orders_by_status(
    user_id: str,
    order_status: OrderStatus,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(db_connect.get_db)
    ):
    """
    Get user orders by status using user_id of the user
    - preparing
    - in_delivery
    - delivered
    - cancelled
    """
    try:
        if limit > 500:
            limit = 500
        
        # التحقق من وجود المستخدم
        user = db.query(User).filter(User.UserID == user_id).first()
        if not user:
            logger.error(f"المستخدم غير موجود - UserID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "المستخدم غير موجود"})
        
        orders = db.query(Order).filter(
            Order.UserID == user_id,
            Order.OrderStatus == order_status
        ).order_by(
            Order.OrderTimestamp.desc()
        ).offset(skip).limit(limit).all()
        
        logger.info(f"تم جلب {len(orders)} طلب بحالة {order_status} للمستخدم {user_id}")
        return orders
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"خطأ في قاعدة البيانات: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "فشل جلب الطلبات"}
        )
        
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "حدث خطأ غير متوقع"}
        )

#=======================================
# 8.PATCH Update Order Status using admin
#========================================

@router.patch("/{order_id}/status", response_model=orders_schema.OrderListResponse)
def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    db: Session = Depends(db_connect.get_db)
    ):
    """
    Update the status of an order using admin:
    - preparing
    - in_delivery
    - delivered
    - cancelled
    """
    
    try:
        order = db.query(Order).filter(Order.OrderID == order_id).first()
        
        if not order:
            logger.error(f"الطلب غير موجود - OrderID: {order_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "الطلب غير موجود"}
            )
        
        old_status = order.OrderStatus
        order.OrderStatus = new_status
        db.commit()
        db.refresh(order)
        
        logger.info(f"تم تحديث حالة الطلب {order_id} من {old_status} إلى {new_status}")
        return order
        
    except HTTPException:
        db.rollback()
        raise
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"خطأ في قاعدة البيانات: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "فشل تحديث حالة الطلب"}
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"خطأ غير متوقع: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "حدث خطأ غير متوقع"}
        )

#=======================================
# 9. GET Orders by Shift ID
#=======================================

@router.get("/shift/{shift_id}", response_model=List[orders_schema.OrderListResponse])
def get_orders_by_shift(
    shift_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(db_connect.get_db)
    ):
    """
    جلب جميع الطلبات المرتبطة بشفت معين
    - يعرض عدد الطلبات
    - يعرض معلومات مبسطة لكل طلب
    """
    try:
        if limit > 500:
            limit = 500
        
        # التحقق من وجود الشفت
        from Database.models.shift_model import Shift
        shift = db.query(Shift).filter(Shift.ShiftID == shift_id).first()
        if not shift:
            logger.error(f"الشفت غير موجود - ShiftID: {shift_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "الشفت غير موجود"}
            )
        
        # جلب الطلبات المرتبطة بالشفت
        orders = db.query(Order).filter(
            Order.ShiftID == shift_id
        ).order_by(
            Order.OrderTimestamp.desc()
        ).offset(skip).limit(limit).all()
        
        logger.info(f"تم جلب {len(orders)} طلب للشفت {shift_id}")
        return orders
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"خطأ في قاعدة البيانات: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "فشل جلب الطلبات"}
        )
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "حدث خطأ غير متوقع"}
        )
