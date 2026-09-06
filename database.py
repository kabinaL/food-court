import sqlite3

DATABASE = "food_court.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():

    connection = get_db_connection()

    # =========================
    # USERS TABLE
    # =========================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            student_id TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)

    # =========================
    # FOODS TABLE
    # =========================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            available INTEGER DEFAULT 1
        )
    """)

    # =========================
    # CART TABLE
    # =========================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            food_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (food_id) REFERENCES foods(id)
        )
    """)

    # =========================
    # ORDERS TABLE
    # =========================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Placed',
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # =========================
    # ORDER ITEMS TABLE
    # =========================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            food_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (food_id) REFERENCES foods(id)
        )
    """)

    # =========================
    # PAYMENTS TABLE
    # =========================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            payment_method TEXT NOT NULL,
            transaction_id TEXT,
            amount REAL NOT NULL,
            payment_status TEXT NOT NULL DEFAULT 'Pending',
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    # =========================
    # INSERT FOOD ITEMS
    # =========================

    food_count = connection.execute(
        "SELECT COUNT(*) FROM foods"
    ).fetchone()[0]

    if food_count == 0:

        foods = [

            (
                "Veg Burger",
                "Fresh vegetable burger with crispy patty",
                80,
                "Fast Food",
                1
            ),

            (
                "Cheese Pizza",
                "Delicious pizza topped with cheese",
                120,
                "Fast Food",
                1
            ),

            (
                "French Fries",
                "Crispy golden french fries",
                60,
                "Snacks",
                1
            ),

            (
                "Fresh Juice",
                "Freshly prepared fruit juice",
                50,
                "Drinks",
                1
            ),

            (
                "Veg Sandwich",
                "Fresh vegetable sandwich",
                70,
                "Snacks",
                1
            ),

            (
                "Masala Dosa",
                "Crispy dosa served with chutney and sambar",
                60,
                "South Indian",
                1
            )

        ]

        connection.executemany("""
            INSERT INTO foods
            (name, description, price, category, available)
            VALUES (?, ?, ?, ?, ?)
        """, foods)

    connection.commit()
    connection.close()


if __name__ == "__main__":

    create_tables()

    print("Database and food items created successfully!")