from sqlmodel import SQLModel, create_engine, Session, select
from app.core.models import Users, Product, Order, Conversation
from app.security import hash_password 
from dotenv import load_dotenv
from faker import Faker
import os
import random

load_dotenv()
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)
fake = Faker()

STATUSES = ["pending", "shipped", "delivered"]

seed_products = [
    Product(name="IPhone 16", price=999.99, specs="Latest model", type="mobile"),
    Product(name="MacBook Pro", price=1999.99, specs="16-inch, M2 chip", type="laptop"),
    Product(name="T-shirt", price=19.99, specs="Cotton, size M", type="clothing"),
    Product(name="Air Conditioner", price=499.99, specs="1.5 ton, energy efficient", type="home_appliance"),
    Product(name="Samsung Galaxy S22", price=899.99, specs="128GB storage, 5G", type="mobile"),
    Product(name="Dell XPS 13", price=1499.99, specs="13-inch, Intel i7", type="laptop"),
    Product(name="Jeans", price=49.99, specs="Denim, size L", type="clothing"),
    Product(name="Microwave Oven", price=199.99, specs="800W, compact", type="home_appliance"),
    Product(name="Google Pixel 7", price=799.99, specs="128GB storage, 5G", type="mobile"),
    Product(name="HP Spectre x360", price=1599.99, specs="15-inch, Intel i7", type="laptop"),
    Product(name="Sweater", price=39.99, specs="Wool, size M", type="clothing"),
    Product(name="Refrigerator", price=999.99, specs="Double door, energy efficient", type="home_appliance")
]

def init_db():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        users = [
            Users(
                name=fake.name(),
                email=fake.email(),
                hashed_password=hash_password(fake.password())
            )
            for _ in range(15)
        ]
        session.add_all(users)
        session.commit()

        for product in seed_products:
            session.add(product)
        session.commit()

        saved_products = session.exec(select(Product)).all()

        for _ in range(15):
            session.add(Order(
                user_id=random.choice(users).user_id,
                product_id=random.choice(saved_products).product_id,
                quantity=random.randint(1, 5),
                status=random.choice(STATUSES)
            ))
        session.commit()

if __name__ == "__main__":
    init_db()
