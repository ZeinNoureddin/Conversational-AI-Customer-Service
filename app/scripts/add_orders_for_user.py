import os
from uuid import uuid4, UUID
from datetime import datetime, timezone

from sqlmodel import Session, select
from app.db.init_db import engine
from app.core.models import Order, Product

USER_ID = UUID("712fb960-661d-4d97-8913-174d793c7e65")

def main():
    with Session(engine) as session:
        # pull some product IDs to use
        products = session.exec(select(Product.product_id)).all()
        if not products:
            print("No products in database—run your seed script first!")
            return

        # create 3 orders for that user, picking random products
        import random
        for _ in range(3):
            prod_id = random.choice(products)
            order = Order(
                order_id=uuid4(),
                user_id=USER_ID,
                product_id=prod_id,
                quantity=random.randint(1, 3),
                status=random.choice(["pending", "shipped", "delivered"]),
                created_at=datetime.now(timezone.utc)
            )
            session.add(order)

        session.commit()
        print("✅ Inserted 5 orders for user", USER_ID)

if __name__ == "__main__":
    # ensure .env is loaded if needed
    from dotenv import load_dotenv
    load_dotenv()
    main()