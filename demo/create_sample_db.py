#!/usr/bin/env python3
"""
Creates a sample SQLite database with realistic e-commerce/manufacturing data
for the SQL Agent demo on Streamlit Cloud.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "sample.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # --- Customers ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            country TEXT,
            segment TEXT,
            created_at TEXT
        )
    """)

    segments = ["Enterprise", "SMB", "Startup", "Government"]
    countries = ["USA", "Germany", "UK", "India", "Serbia", "Canada", "Australia", "Japan", "Brazil", "France"]
    first_names = ["Alice", "Bob", "Carlos", "Diana", "Erik", "Fatima", "George", "Hannah", "Ivan", "Julia",
                   "Kenji", "Lara", "Miguel", "Nina", "Oscar", "Priya", "Quinn", "Rosa", "Stefan", "Tanya"]
    last_names = ["Smith", "Mueller", "Patel", "Johnson", "Williams", "Brown", "Garcia", "Kim", "Chen", "Silva",
                  "Anderson", "Taylor", "Thomas", "Jackson", "White", "Harris", "Martin", "Clark", "Lewis", "Hall"]

    customers = []
    for i in range(1, 201):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"{name.lower().replace(' ', '.')}@example.com"
        country = random.choice(countries)
        segment = random.choice(segments)
        created = (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 730))).strftime("%Y-%m-%d")
        customers.append((i, name, email, country, segment, created))

    c.executemany("INSERT OR REPLACE INTO customers VALUES (?,?,?,?,?,?)", customers)

    # --- Products ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            unit_price REAL,
            cost REAL,
            stock_qty INTEGER
        )
    """)

    categories = {
        "Electronics": [("Wireless Headphones", 79.99, 32), ("USB-C Hub", 49.99, 22), ("Mechanical Keyboard", 129.99, 55),
                        ("4K Monitor", 399.99, 180), ("Webcam Pro", 89.99, 38), ("Portable SSD 1TB", 109.99, 48),
                        ("Smart Speaker", 59.99, 25), ("Gaming Mouse", 69.99, 30)],
        "Software": [("Cloud Backup Plan", 9.99, 0), ("Antivirus Suite", 39.99, 5), ("Project Manager Pro", 19.99, 2),
                     ("Design Toolkit", 59.99, 8), ("Code Editor License", 29.99, 3), ("VPN Service Annual", 49.99, 5)],
        "Services": [("IT Consulting Hour", 150.00, 0), ("Data Migration Package", 2500.00, 800),
                     ("Security Audit", 5000.00, 1500), ("Custom Development", 120.00, 40),
                     ("Training Workshop", 800.00, 200), ("Support Plan Monthly", 299.99, 80)],
        "Hardware": [("Server Rack Unit", 1200.00, 650), ("Network Switch 24-port", 349.99, 160),
                     ("UPS Battery Backup", 249.99, 110), ("Cable Kit Bundle", 29.99, 8),
                     ("Rack Mount Rails", 49.99, 18), ("Cooling Fan Module", 89.99, 35)]
    }

    products = []
    pid = 1
    for cat, items in categories.items():
        for name, price, cost in items:
            stock = random.randint(5, 500)
            products.append((pid, name, cat, price, cost, stock))
            pid += 1

    c.executemany("INSERT OR REPLACE INTO products VALUES (?,?,?,?,?,?)", products)

    # --- Orders ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            status TEXT,
            total_amount REAL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)

    # --- Order Items ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            item_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price REAL,
            discount REAL DEFAULT 0,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    statuses = ["Completed", "Completed", "Completed", "Shipped", "Shipped", "Processing", "Cancelled"]
    orders = []
    items = []
    item_id = 1

    for oid in range(1, 1501):
        cid = random.randint(1, 200)
        order_date = (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 500))).strftime("%Y-%m-%d")
        status = random.choice(statuses)
        total = 0.0

        num_items = random.randint(1, 5)
        for _ in range(num_items):
            prod = random.choice(products)
            qty = random.randint(1, 10)
            price = prod[3]
            discount = random.choice([0, 0, 0, 0.05, 0.10, 0.15])
            line_total = qty * price * (1 - discount)
            total += line_total
            items.append((item_id, oid, prod[0], qty, price, discount))
            item_id += 1

        orders.append((oid, cid, order_date, status, round(total, 2)))

    c.executemany("INSERT OR REPLACE INTO orders VALUES (?,?,?,?,?)", orders)
    c.executemany("INSERT OR REPLACE INTO order_items VALUES (?,?,?,?,?,?)", items)

    # --- Employees ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            role TEXT,
            hire_date TEXT,
            salary REAL
        )
    """)

    departments = {
        "Engineering": ["Software Engineer", "Senior Engineer", "Tech Lead", "DevOps Engineer"],
        "Sales": ["Account Executive", "Sales Manager", "Business Development Rep"],
        "Marketing": ["Marketing Specialist", "Content Manager", "SEO Analyst"],
        "Support": ["Support Agent", "Support Lead", "Customer Success Manager"],
        "Operations": ["Operations Manager", "Data Analyst", "Project Manager"]
    }

    employees = []
    eid = 1
    for dept, roles in departments.items():
        for _ in range(random.randint(3, 8)):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            role = random.choice(roles)
            hire_date = (datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1800))).strftime("%Y-%m-%d")
            salary = round(random.uniform(45000, 150000), 2)
            employees.append((eid, name, dept, role, hire_date, salary))
            eid += 1

    c.executemany("INSERT OR REPLACE INTO employees VALUES (?,?,?,?,?,?)", employees)

    conn.commit()
    conn.close()
    print(f"Sample database created at {DB_PATH}")
    print(f"  - {len(customers)} customers")
    print(f"  - {len(products)} products")
    print(f"  - {len(orders)} orders")
    print(f"  - {len(items)} order items")
    print(f"  - {len(employees)} employees")


if __name__ == "__main__":
    create_database()
