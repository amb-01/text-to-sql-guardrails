from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ecommerce")

def init_db():
    engine = create_engine(DATABASE_URL)
    
    schema_sql = """
    DROP TABLE IF EXISTS orders CASCADE;
    DROP TABLE IF EXISTS products CASCADE;
    DROP TABLE IF EXISTS users CASCADE;

    CREATE TABLE users (
        user_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        signup_date DATE NOT NULL
    );

    CREATE TABLE products (
        product_id SERIAL PRIMARY KEY,
        product_name VARCHAR(150) NOT NULL,
        category VARCHAR(50) NOT NULL,
        price NUMERIC(10, 2) NOT NULL
    );

    CREATE TABLE orders (
        order_id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
        product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
        order_date DATE NOT NULL,
        quantity INT NOT NULL
    );

    INSERT INTO users (name, email, signup_date) VALUES
    ('Alice Smith', 'alice@example.com', '2023-01-15'),
    ('Bob Jones', 'bob@example.com', '2023-03-22'),
    ('Charlie Brown', 'charlie@example.com', '2023-05-10');

    INSERT INTO products (product_name, category, price) VALUES
    ('Mechanical Keyboard', 'Electronics', 120.00),
    ('Ergonomic Mouse', 'Electronics', 60.00),
    ('Coffee Mug', 'Kitchen', 15.50);

    INSERT INTO orders (user_id, product_id, order_date, quantity) VALUES
    (1, 1, '2023-10-01', 1),
    (1, 3, '2023-10-02', 2),
    (2, 2, '2023-10-05', 1);
    """

    with engine.begin() as conn:
        conn.execute(text(schema_sql))
    print("PostgreSQL tables created and seeded successfully.")

if __name__ == "__main__":
    init_db()