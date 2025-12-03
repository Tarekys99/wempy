"""
- تعريف الجداول using SQLAlchemy ORM
- المجلد دا لإنشاء نماذج جداول قاعدة البيانات لكل قسم

"""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func
from sqlalchemy.types import TypeDecorator, CHAR
from typing import List
from datetime import datetime
import uuid

from ..db_connect import Base


# Custom UUID type for SQLite compatibility
class GUID(TypeDecorator):
    """Platform-independent GUID type. Uses CHAR(36) for SQLite."""
    impl = CHAR
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value


"""
class user:
     id str pk
     FName str not null
     LName str not null
     phoneNumber str not null unique
"""

class User(Base):
    __tablename__ = "users"
    UserID: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
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
