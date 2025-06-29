from sqlmodel import Session, select
from app.core.models import Users, Order, Product, Conversation
from app.db.init_db import engine
from typing import Optional

VALID_PRODUCT_TYPES = {"type1", "type2", "type3"}  # Define your valid product types here


def get_order(order_id: str):
    if not isinstance(order_id, str):
        raise ValueError("order_id must be a string")
    with Session(engine) as session:
        order = session.exec(select(Order).where(Order.order_id == order_id)).first()
        if not order:
            raise ValueError(f"No order found with ID {order_id}")
        return order


def get_my_orders(user_id: str):
    if not isinstance(user_id, str):
        raise ValueError("user_id must be a string")
    with Session(engine) as session:
        orders = session.exec(select(Order).where(Order.user_id == user_id)).all()
        if not orders:
            raise ValueError(f"No orders found for user ID {user_id}")
        return orders


def update_profile(user_id: str, updates: dict):
    if not isinstance(user_id, str):
        raise ValueError("user_id must be a string")
    if not isinstance(updates, dict):
        raise ValueError("updates must be a dictionary")
    valid_fields = {"name", "email", "hashed_password"}
    for key in updates.keys():
        if key not in valid_fields:
            raise ValueError(f"Invalid field: {key}")
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.user_id == user_id)).first()
        if not user:
            raise ValueError(f"No user found with ID {user_id}")
        for key, value in updates.items():
            setattr(user, key, value)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def search_products(product_type: str, price_filter: Optional[tuple] = None):
    if product_type not in VALID_PRODUCT_TYPES:
        raise ValueError(f"Invalid product type: {product_type}")
    if price_filter:
        if not isinstance(price_filter, tuple) or len(price_filter) != 2:
            raise ValueError("price_filter must be a tuple with two values (min_price, max_price)")
        if not all(isinstance(price, (int, float)) for price in price_filter):
            raise ValueError("price_filter values must be integers or floats")
    with Session(engine) as session:
        stmt = select(Product).where(Product.type == product_type)
        if price_filter:
            stmt = stmt.where(Product.price >= price_filter[0], Product.price <= price_filter[1])
        results = session.exec(stmt).all()
        return results


def save_conversation(user_id: str, message: str, direction: str) -> None:
    conv = Conversation(user_id=user_id, message=message, direction=direction)
    with Session(engine) as session:
        session.add(conv)
        session.commit()