from sqlmodel import Session, select
from app.db.models import Users, Order, Product, Conversation
from app.db.init_db import engine


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

def search_products(query: str):
    with Session(engine) as session:
        results = session.exec(select(Product).where(Product.name.ilike(f"%{query}%"))).all()
        return results

def save_conversation(user_id: str, message: str, direction: str) -> None:
    conv = Conversation(user_id=user_id, message=message, direction=direction)
    with Session(engine) as session:
        session.add(conv)
        session.commit()