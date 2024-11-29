import sqlite3
import pandas as pd
import os

DATABASE = "ecommerce.db"

# Function to create the SQLite database and tables
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            password TEXT,
            name TEXT,
            email TEXT,
            address TEXT,
            phone_number TEXT
        )
    ''')

    # Create orders table with foreign key to customers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            order_date TEXT,
            quantity INTEGER,
            total_price REAL,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')

    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL,
            stock INTEGER
        )
    ''')

    # Create a many-to-many relationship table between orders and products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            rating INTEGER,
            review_text TEXT,
            review_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')

    conn.commit()
    conn.close()

# Function to load CSV data into the SQLite database
def load_csv_to_db(csv_file, table_name):
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file '{csv_file}' not found")
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Insert each row into the corresponding table
    for _, row in df.iterrows():
        # Prepare the values based on the table
        if table_name == "users":
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, password, name, email, address, phone_number)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['user_id'], row['password'], row['name'], row['email'], row['address'], row['phone_number']))

        elif table_name == "orders":
            cursor.execute('''
                INSERT OR REPLACE INTO orders (order_id, user_id, product_id, order_date, quantity, total_price, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (row['order_id'], row['user_id'], row['product_id'], row['order_date'], row['quantity'], row['total_price'], row['status']))

        elif table_name == "reviews":
            cursor.execute('''
                INSERT OR REPLACE INTO reviews (review_id, user_id, product_id, rating, review_text, review_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['review_id'], row['user_id'], row['product_id'], row['rating'], row['review_text'], row['review_date']))



        elif table_name == "products":
            cursor.execute('''
                INSERT OR REPLACE INTO products (product_id, name, category, price, stock)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['product_id'], row['name'], row['category'], row['price'], row['stock']))

        conn.commit()

    conn.close()

# Main function to initialize the database and load CSV data
def setup():
    # Initialize the database (create tables)
    init_db()

    # Paths to the CSV files
    users_csv = "./csvs/users.csv"
    products_csv = "./csvs/products.csv"
    orders_csv = "./csvs/orders.csv"
    reviews_csv = "./csvs/reviews.csv"

    # Load data into the database
    load_csv_to_db(users_csv, "users")
    load_csv_to_db(products_csv, "products")
    load_csv_to_db(orders_csv, "orders")
    load_csv_to_db(reviews_csv, "reviews")

    print("Data has been successfully inserted into the database.")

if __name__ == "__main__":
    setup()
