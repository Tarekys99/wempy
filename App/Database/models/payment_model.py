from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from ..db_connect import Base

class PaymentMethod(Base):
    __tablename__ = "payment_method"
    PaymentID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    PaymentName: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    IsActive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    """
    Relationships:
    - 'one-to-many' with 'orders' table relation = Mapped[class name]
    """
    orders: Mapped[List["Order"]] = relationship(back_populates="payment_method")

    def __repr__(self):
        return f"<PaymentMethod name='{self.PaymentName}', active='{self.IsActive}')>"