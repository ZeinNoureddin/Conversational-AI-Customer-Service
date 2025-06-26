from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import uuid4, UUID
from datetime import datetime, timezone

class User(SQLModel, table=True):
    user_id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Product(SQLModel, table=True):
    product_id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    price: float
    specs: Optional[str]
    in_stock: bool = True

class Order(SQLModel, table=True):
    order_id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.user_id")
    product_id: UUID = Field(foreign_key="product.product_id")
    quantity: int
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Conversation(SQLModel, table=True):
    conv_id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.user_id")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: str
    direction: str  # 'user' or 'agent'