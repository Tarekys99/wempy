from sqlalchemy import Integer, ForeignKey, DECIMAL, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from ..db_connect import Base

class OrderItem(Base):
    __tablename__ = "order_items"
    
    OrderItemID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    OrderID: Mapped[int] = mapped_column(Integer, ForeignKey("orders.OrderID", ondelete="CASCADE"), nullable=False)
    VariantID: Mapped[int] = mapped_column(Integer, ForeignKey("product_variants.VariantID", ondelete="RESTRICT"), nullable=False)
    Quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    UnitPrice: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    Subtotal: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    IsSada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    """
    Relationships:
    - 'many-to-one' with 'orders' table
    - 'many-to-one' with 'variants' table
    """
    orders: Mapped["Order"] = relationship(back_populates="order_items")
    product_variants: Mapped["ProductVariant"] = relationship(back_populates="order_items")
    
    def __repr__(self):
        return f"<(OrderItem OrderItemID={self.OrderItemID}, VariantID={self.VariantID})>"