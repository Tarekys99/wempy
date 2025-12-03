from sqlalchemy import String, Integer, Text, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from decimal import Decimal

from ..db_connect import Base

#==============================
# Category table
#==============================
class Category(Base):
     __tablename__ = "categories"
     CategoryID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
     CategoryName: Mapped[str] = mapped_column(String(50),nullable=False, unique=True)

     """
     'one-to-many' with products table, Mapped[class name]
     """
     products: Mapped[List["Products"]] = relationship(
          back_populates="categories",
          cascade="all, delete-orphan"
     )
     def __repr__(self):
        return f"<categories(id={self.CategoryID}, name='{self.CategoryName}')>"
        
#==============================
# Products table
#==============================
class Products(Base):
     __tablename__ = "products"
     ProductID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
     CategoryID: Mapped[int] = mapped_column(Integer, ForeignKey("categories.CategoryID"), nullable=False)
     Name: Mapped[str] = mapped_column(String(50), nullable=False)
     Description: Mapped[str] = mapped_column(Text)
     ImageUrl: Mapped[str] = mapped_column(String(255),nullable=False)

     """
     Relationships:
     - 'many-to-one' with 'categories' table / اسم العلاقة "categories" or any name
     - 'one-to-many' with 'product_variants' table / اسم العلاقة "product_variants" or any name
     """
     categories: Mapped["Category"] = relationship(back_populates="products")

     product_variants: Mapped[List["ProductVariant"]] = relationship(
          back_populates="products",
          cascade="all, delete-orphan")
          
     def __repr__(self):
          return f"<products(id={self.ProductID}, name='{self.Name}')>"

#==============================
# ProductVariant table
#==============================
class ProductVariant(Base):
     __tablename__ = "product_variants"
     VariantID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
     ProductID: Mapped[int] = mapped_column(Integer, ForeignKey("products.ProductID"), nullable=False)
     SizeID: Mapped[int] = mapped_column(Integer, ForeignKey("sizes.SizeID"), nullable=False)
     TypeID: Mapped[int] = mapped_column(Integer, ForeignKey("types.TypeID"), nullable=False)
     Price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
     IsAvailable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

     """
     Relationships:
     - 'one-to-many' with sizes/types tables
     - 'many-to-one' with products table
     - one-to-many with order_items
     """
     products: Mapped["Products"] = relationship(back_populates="product_variants")
     sizes: Mapped["Sizes"] = relationship(back_populates="product_variants")
     types: Mapped["Types"] = relationship(back_populates="product_variants")
     order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product_variants")

     def __repr__(self):
          return f"<ProductVariant(id={self.VariantID}, Price={self.Price})>"

#==============================
# Sizes table
#==============================
class Sizes(Base):
     __tablename__ = "sizes"
     SizeID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
     SizeName: Mapped[str] = mapped_column(String(50),nullable=False, unique=True)

     product_variants: Mapped[List["ProductVariant"]] = relationship(back_populates="sizes")

     def __repr__(self):
          return f"<Size(id={self.SizeID}, name='{self.SizeName}')>"

#==============================
# Types table
#==============================
class Types(Base):
     __tablename__ = "types"
     TypeID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
     TypeName: Mapped[str] = mapped_column(String(50),nullable=False, unique=True)

     product_variants: Mapped[List["ProductVariant"]] = relationship(back_populates="types")

     def __repr__(self):
          return f"<Type(id={self.TypeID}, name='{self.TypeName}')>"
