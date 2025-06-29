from sqlmodel import Session, select
from app.core.models import Users, Order, Product, Conversation
from app.db.init_db import engine
from typing import Optional


def get_order(order_id: str):
    with Session(engine) as session:
        order = session.exec(select(Order).where(Order.order_id == order_id)).first()
        return order

def get_my_orders(user_id: str):
    with Session(engine) as session:
        orders = session.exec(select(Order).where(Order.user_id == user_id)).all()
        return orders

def update_profile(user_id: str, updates: dict):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.user_id == user_id)).first()
        if not user:
            return None
        for key, value in updates.items():
            setattr(user, key, value)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def search_products(product_type: str = None, price_filter: Optional[tuple] = None):
    with Session(engine) as session:
        stmt = select(Product)
        stmt = stmt.where(Product.type == product_type)
        if price_filter:
            stmt = stmt.where(Product.price >= price_filter[0], Product.price <= price_filter[1])
        results = session.exec(stmt).all()
        return results

def save_conversation(user_id: str, message: str, direction: str) -> None:
    conv = Conversation(user_id=user_id, message=message, direction=direction)
    with Session(engine) as session:
        session.add(conv)
        session.commit()