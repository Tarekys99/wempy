from sqlalchemy import String, Integer, Text, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from decimal import Decimal
import uuid

from ..db_connect import Base
from .user_model import GUID

#==============================
# Address table
#==============================
class Address(Base):
    __tablename__ = "address"
    AddressID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    UserID: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.UserID"), nullable=False)

    RecipientName: Mapped[str] = mapped_column(String(50), nullable=False)
    Street: Mapped[str] = mapped_column(String(100), nullable=False)
    Building: Mapped[str] = mapped_column(String(100), nullable=False)
    City: Mapped[str] = mapped_column(String(100), nullable=False)
    RecipientPhone: Mapped[str] = mapped_column(String(20), nullable=False)
    Phone2: Mapped[str | None] = mapped_column(String(20), nullable=True)
    DeliveryNotes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ZoneID: Mapped[int] = mapped_column(Integer, ForeignKey("delivery_zone.ZoneID"), nullable=False)

    """
    Relationships:
    - 'many-to-one' with 'users' table
    - 'many-to-one' with 'delivery_zones' table = Mapped[class name]
    - 'one-to-many' with orders table
    """
    users: Mapped["User"] = relationship(back_populates="address")
    delivery_zone: Mapped["DeliveryZone"] = relationship(back_populates="address")
    orders: Mapped[List["Order"]] =  relationship(back_populates="address")

    def __repr__(self):
        return f"<Address(id={self.AddressID}, recipient_name='{self.RecipientName}')>"

#==============================
# DeliveryZone table
#==============================
class DeliveryZone(Base):
    __tablename__ = "delivery_zone"
    ZoneID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ZoneName: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    DeliveryCost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    """
    Relationships:
    - 'one-to-many' with 'address' table
    """
    address: Mapped[List["Address"]] = relationship(
        back_populates="delivery_zone",
        cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"<DeliveryZone(id={self.ZoneID}, name='{self.ZoneName}', cost={self.DeliveryCost})>"