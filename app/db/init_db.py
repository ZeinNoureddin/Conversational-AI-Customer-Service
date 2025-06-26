# from sqlmodel import SQLModel, create_engine
# from .models import User, Product, Order, Conversation
# import os
# from dotenv import load_dotenv

# load_dotenv()
# database_url = os.getenv("DATABASE_URL")
# engine = create_engine(database_url)

# def init_db():
#     SQLModel.metadata.create_all(engine)

# if __name__ == "__main__":
#     init_db()

from sqlmodel import SQLModel, create_engine, Session
from app.db.models import User, Product, Order, Conversation
import os
from dotenv import load_dotenv
from faker import Faker
import random
import json

load_dotenv()
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)
fake = Faker()

STATUSES = ["pending", "shipped", "delivered"]

def init_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        users = [User(name=fake.name(), email=fake.email()) for _ in range(15)]
        session.add_all(users)
        session.commit()

        products = [
            Product(
                name=fake.word().capitalize() + " Pro",
                price=round(random.uniform(100, 2000), 2),
                specs=json.dumps({"ram": f"{random.choice([8, 16, 32])}GB", "color": fake.color_name()}),
                in_stock=random.choice([True, True, True, False])
            ) for _ in range(15)
        ]
        session.add_all(products)
        session.commit()

        for _ in range(15):
            session.add(Order(
                user_id=random.choice(users).user_id,
                product_id=random.choice(products).product_id,
                quantity=random.randint(1, 5),
                status=random.choice(STATUSES)
            ))
        session.commit()

if __name__ == "__main__":
    init_db()
