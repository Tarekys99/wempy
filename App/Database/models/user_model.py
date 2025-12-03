"""
- تعريف الجداول using SQLAlchemy ORM
- المجلد دا لإنشاء نماذج جداول قاعدة البيانات لكل قسم

"""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from typing import List
from datetime import datetime
import uuid

from ..db_connect import Base


"""
class user:
     id str pk
     FName str not null
     LName str not null
     phoneNumber str not null unique
"""

class User(Base):
    __tablename__ = "users"
    UserID: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    FName: Mapped[str] = mapped_column(nullable=False)
    LName: Mapped[str] = mapped_column(nullable=False)
    PhoneNumber: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    Email: Mapped[str] = mapped_column(String, nullable=True)
    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    lastLogin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships:
    # - 'one-to-many' with 'oders' table
    # - 'one-to-many' with 'adderss' table
    # relation name: Mapped['class name'] = relationship('other relation name' in other db model)

    orders: Mapped[List["Order"]] = relationship(back_populates="users")
    
    address: Mapped[List["Address"]] = relationship(back_populates="users")
    
    def __repr__(self):
        return f"<User(UserID={self.UserID}, phone={self.PhoneNumber})>"
