from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=2000)
    category: str = Field(min_length=1, max_length=80)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0)
    image_url: HttpUrl | None = None


class Product(ProductCreate):
    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)


class UserRole(str, Enum):
    customer = "cliente"
    administrator = "administrador"


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)


class User(UserCreate):
    id: str
    role: UserRole = UserRole.customer
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)


class OrderItemCreate(BaseModel):
    product_id: str = Field(pattern=r"^[0-9a-fA-F]{24}$")
    quantity: int = Field(gt=0)


class OrderLineItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    cancelled = "cancelled"


class OrderCreate(BaseModel):
    customer_id: str = Field(pattern=r"^[0-9a-fA-F]{24}$")
    items: list[OrderItemCreate] = Field(min_length=1)

    @field_validator("items")
    @classmethod
    def validate_unique_products(cls, items: list[OrderItemCreate]) -> list[OrderItemCreate]:
        product_ids = [item.product_id.lower() for item in items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Un pedido no puede repetir el mismo producto.")
        return items


class Order(BaseModel):
    id: str
    customer_id: str
    items: list[OrderLineItem]
    total: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    status: OrderStatus = OrderStatus.pending
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)
