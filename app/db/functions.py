from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.core.models import Users, Order, Product, Conversation
from app.db.init_db import engine
from typing import Optional

VALID_PRODUCT_TYPES = {"mobile", "laptop", "clothing", "home_appliance"}

def get_order(order_id: str):
    if not isinstance(order_id, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="order_id must be a string"
        )
    with Session(engine) as session:
        order = session.exec(select(Order).where(Order.order_id == order_id)).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No order found with ID {order_id}"
            )
        return order


def get_my_orders(user_id: str):
    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id must be a string"
        )
    with Session(engine) as session:
        orders = session.exec(select(Order).where(Order.user_id == user_id)).all()
        if not orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No orders found for user ID {user_id}"
            )
        return orders


def update_profile(current_user_id: str, new_email: str):
    if not isinstance(current_user_id, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="current_user_id must be a string"
        )
    if not isinstance(new_email, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="new_email must be a string"
        )

    with Session(engine) as session:
        existing = session.exec(
            select(Users).where(Users.email == new_email)
        ).first()
        if existing and existing.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email is already in use."
            )

        user = session.exec(
            select(Users).where(Users.user_id == current_user_id)
        ).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user found with ID {current_user_id}"
            )

        user.email = new_email
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def search_products(product_type: str, price_filter: Optional[tuple] = None):
    if product_type not in VALID_PRODUCT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid product type: {product_type}"
        )
    if price_filter:
        if isinstance(price_filter, list):
            price_filter = tuple(price_filter)
        if not isinstance(price_filter, tuple) or len(price_filter) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="price_filter must be a tuple with two values (min_price, max_price)"
            )
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