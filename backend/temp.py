import pandas as pd
import random
from faker import Faker

# Initialize Faker
fake = Faker()

# Generate users data
users = []
for user_id in range(1, 1001):
    users.append({
        "user_id": user_id,
        "password": fake.password(),
        "name": fake.name(),
        "email": fake.email(),
        "address": fake.address(),
        "phone_number": fake.phone_number()
    })

users_df = pd.DataFrame(users)

# Generate products data
products = []
for product_id in range(1, 1001):
    products.append({
        "product_id": product_id,
        "name": fake.word(),
        "category": fake.word(),
        "price": round(random.uniform(5, 500), 2),
        "stock": random.randint(10, 1000)
    })

products_df = pd.DataFrame(products)

# Generate orders data
orders = []
for order_id in range(1, 1001):
    orders.append({
        "order_id": order_id,
        "user_id": random.randint(1, 1000),
        "product_id": random.randint(1, 1000),
        "order_date": fake.date_this_year(),
        "quantity": random.randint(1, 5),
        "total_price": round(random.uniform(10, 1000), 2),
        "status": random.choice(["Pending", "Shipped", "Delivered", "Cancelled"])
    })

orders_df = pd.DataFrame(orders)

# Generate reviews data
reviews = []
for review_id in range(1, 1001):
    reviews.append({
        "review_id": review_id,
        "user_id": random.randint(1, 1000),
        "product_id": random.randint(1, 1000),
        "rating": random.randint(1, 5),
        "review_text": fake.sentence(),
        "review_date": fake.date_this_year()
    })

reviews_df = pd.DataFrame(reviews)

# Save data to CSV files
users_df.to_csv("users.csv", index=False)
products_df.to_csv("products.csv", index=False)
orders_df.to_csv("orders.csv", index=False)
reviews_df.to_csv("reviews.csv", index=False)

print("Data generation complete. Files saved: users.csv, products.csv, orders.csv, reviews.csv")
