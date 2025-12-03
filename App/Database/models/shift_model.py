from sqlalchemy import Integer, String, Date, Time, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, time
from typing import List

from ..db_connect import Base

class Shift(Base):
    __tablename__ = "shifts"
    
    ShiftID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Shift_Date: Mapped[date] = mapped_column(Date, nullable=False,index=True)
    Shift_Number: Mapped[str] = mapped_column(String(10), nullable=False)

    Start_Time: Mapped[time] = mapped_column(Time, nullable=False)
    End_Time: Mapped[time | None] = mapped_column(Time, nullable=True) # ✅ يمكن أن يكون NULL لانه نهاية الوردية
    
    IsActive: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=True, 
        server_default="true")
    
    # ✅ Constraint: PK in 2 table
    __table_args__ = (
        UniqueConstraint(
            'Shift_Date', 
            'Shift_Number', 
            name='unique_daily_shift'),
    )
    
    """
    Relationships:
    - 'one-to-many' with 'orders' table 
    """
    orders: Mapped[List["Order"]] = relationship(back_populates="shifts")
    
    def __repr__(self):
        status = "مفتوحة" if self.End_Time is None else "منتهية"
        return (
            f"<Shift {self.Shift_Number} on {self.Shift_Date}, "
            f"Status={status}>"
        )
    
    @property
    def is_open(self) -> bool:
        """التحقق من أن الوردية مفتوحة"""
        return self.End_Time is None
    