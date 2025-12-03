# orders_info_model.py
from sqlalchemy import Integer, Numeric, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum
import uuid
from typing import List

from ..db_connect import Base
from .user_model import GUID

"""
معلومات عامة عن الاوردر:
✅ معلومات الطلب العامة (Header)
✅ من قام بالطلب؟
✅ أين سيتم التوصيل؟
✅ كيف سيدفع؟
✅ ما هي الحالة؟
✅ كم السعر الإجمالي؟

"""

class OrderStatus(enum.Enum):
    PREPARING = "preparing"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"  
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    
    # Primary Key
    OrderID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    UserID: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.UserID"), nullable=False)
    AddressID: Mapped[int] = mapped_column(Integer, ForeignKey("address.AddressID"), nullable=False)
    PaymentID: Mapped[int] = mapped_column(Integer, ForeignKey("payment_method.PaymentID"), nullable=False)
    ShiftID: Mapped[int] = mapped_column(Integer, ForeignKey("shifts.ShiftID"), nullable=False)
    
    # Order Information
    OrderNumber: Mapped[int] = mapped_column(Integer, nullable=False)
    OrderTimestamp: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False,
        comment="وقت إنشاء الطلب")
    
    # Pricing
    DeliveryFee: Mapped[float] = mapped_column(
        Numeric(10, 2), 
        nullable=False, 
        default=0.0,
        comment="رسوم التوصيل")

    TotalPrice: Mapped[float] = mapped_column(
        Numeric(10, 2), 
        nullable=False,
        comment="السعر الإجمالي" )

    # Status
    OrderStatus: Mapped['OrderStatus'] = mapped_column(
        SQLEnum(OrderStatus, name="order_status_enum", create_constraint=True),
        nullable=False,
        default=OrderStatus.PREPARING,
        comment="حالة الطلب الحالية"
    )
    
    OrderNotes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ExternalNotes: Mapped[str | None] = mapped_column(Text, nullable=True)
    

    """
    Relationships:
    - 'many-to-one' with 'users' table
    - 'many-to-one' with 'address' table
    - 'many-to-one' with 'payment_method' table
    - 'many-to-one' with 'shifts' table
    - 'one-to-many' with 'order_items' table
    """
    users: Mapped["User"] = relationship(back_populates="orders")

    address: Mapped["Address"] = relationship(back_populates="orders")

    payment_method: Mapped["PaymentMethod"] = relationship(back_populates="orders")

    shifts: Mapped["Shift"] = relationship(back_populates="orders")

    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="orders")
    
    def __repr__(self):
        return (
            f"<Order ID={self.OrderID}, "
            f"Number={self.OrderNumber}, "
            f"Status={self.OrderStatus.value}>"
        )
    
    @property
    def is_completed(self) -> bool:
        """هل الطلب مكتمل (تم توصيله)؟"""
        return self.OrderStatus == OrderStatus.DELIVERED
    
    @property
    def is_cancelled(self) -> bool:
        """هل الطلب ملغي؟"""
        return self.OrderStatus == OrderStatus.CANCELLED
    