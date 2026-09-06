from flask import Flask, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

from database import get_db_connection, create_tables


app = Flask(__name__)
app.secret_key = "food_court_secret_key_2026"

# Create database tables
create_tables()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user_id" in session:

        if session.get("role") == "admin":
            return redirect(url_for("admin_dashboard"))

        return redirect(url_for("user_dashboard"))

    return redirect(url_for("login"))


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter email and password.")
            return redirect(url_for("login"))

        connection = get_db_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if user is None:
            flash("Invalid email or password.")
            return redirect(url_for("login"))

        try:
            password_correct = check_password_hash(
                user["password"],
                password
            )
        except Exception:
            password_correct = False

        if not password_correct:
            flash("Invalid email or password.")
            return redirect(url_for("login"))

        # Create session only after successful login
        session.clear()

        session["user_id"] = user["id"]
        session["full_name"] = user["full_name"]
        session["email"] = user["email"]
        session["role"] = user["role"]

        if user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))

        return redirect(url_for("user_dashboard"))

    return render_template("login.html")


# =========================================================
# ACCOUNT TYPE
# =========================================================

@app.route("/account-type")
def account_type():

    # IMPORTANT:
    # Do NOT redirect based on existing session here.
    # This page must be accessible from the login page.

    return render_template("account_type.html")


# =========================================================
# USER SIGNUP
# =========================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "GET":
        return render_template("signup.html")

    # -----------------------------------------------------
    # GET FORM DATA
    # -----------------------------------------------------

    full_name = request.form.get(
        "full_name",
        ""
    ).strip()

    student_id = request.form.get(
        "student_id",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not all([
        full_name,
        student_id,
        email,
        phone,
        password,
        confirm_password
    ]):
        flash("Please fill in all fields.")
        return redirect(url_for("signup"))

    if password != confirm_password:
        flash("Passwords do not match.")
        return redirect(url_for("signup"))

    if len(password) < 6:
        flash("Password must contain at least 6 characters.")
        return redirect(url_for("signup"))

    # -----------------------------------------------------
    # DATABASE CONNECTION
    # -----------------------------------------------------

    connection = get_db_connection()

    # -----------------------------------------------------
    # CHECK DUPLICATE EMAIL
    # -----------------------------------------------------

    existing_email = connection.execute(
        """
        SELECT id
        FROM users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    if existing_email:
        connection.close()
        flash("Email already exists.")
        return redirect(url_for("signup"))

    # -----------------------------------------------------
    # CHECK DUPLICATE STUDENT ID
    # -----------------------------------------------------

    existing_student = connection.execute(
        """
        SELECT id
        FROM users
        WHERE student_id = ?
        """,
        (student_id,)
    ).fetchone()

    if existing_student:
        connection.close()
        flash("Student ID already exists.")
        return redirect(url_for("signup"))

    # -----------------------------------------------------
    # HASH PASSWORD
    # -----------------------------------------------------

    hashed_password = generate_password_hash(password)

    # -----------------------------------------------------
    # INSERT USER
    # -----------------------------------------------------

    connection.execute(
        """
        INSERT INTO users
        (
            full_name,
            student_id,
            email,
            phone,
            password,
            role
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            full_name,
            student_id,
            email,
            phone,
            hashed_password,
            "user"
        )
    )

    connection.commit()
    connection.close()

    # IMPORTANT:
    # A newly registered user is NOT logged in automatically.
    session.clear()

    flash(
        "Account created successfully. Please login."
    )

    return redirect(url_for("login"))


# =========================================================
# ADMIN SIGNUP
# =========================================================

@app.route("/admin-signup", methods=["GET", "POST"])
def admin_signup():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not all([
            full_name,
            email,
            phone,
            password,
            confirm_password
        ]):
            flash("Please fill in all fields.")
            return redirect(url_for("admin_signup"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("admin_signup"))

        if len(password) < 6:
            flash("Password must contain at least 6 characters.")
            return redirect(url_for("admin_signup"))

        connection = get_db_connection()

        existing_user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user:
            connection.close()
            flash("Email already exists.")
            return redirect(url_for("admin_signup"))

        hashed_password = generate_password_hash(password)

        # Student ID is generated for admin
        admin_student_id = "ADMIN-" + email.split("@")[0]

        # Make sure generated ID is unique
        counter = 1
        original_id = admin_student_id

        while connection.execute(
            "SELECT id FROM users WHERE student_id = ?",
            (admin_student_id,)
        ).fetchone():

            admin_student_id = f"{original_id}-{counter}"
            counter += 1

        connection.execute(
            """
            INSERT INTO users
            (
                full_name,
                student_id,
                email,
                phone,
                password,
                role
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                full_name,
                admin_student_id,
                email,
                phone,
                hashed_password,
                "admin"
            )
        )

        connection.commit()
        connection.close()

        flash("Admin account created successfully.")
        return redirect(url_for("login"))

    return render_template("admin_signup.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.")

    return redirect(url_for("login"))


# =========================================================
# USER DASHBOARD
# =========================================================

@app.route("/user-dashboard")
def user_dashboard():

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    connection = get_db_connection()

    foods = connection.execute(
        """
        SELECT *
        FROM foods
        WHERE available = 1
        ORDER BY id DESC
        """
    ).fetchall()

    cart_count = connection.execute(
        """
        SELECT COALESCE(SUM(quantity), 0) AS count
        FROM cart
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()["count"]

    connection.close()

    return render_template(
        "user_dashboard.html",
        foods=foods,
        cart_count=cart_count
    )


# =========================================================
# MENU
# =========================================================

@app.route("/menu")
def menu():

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    category = request.args.get(
        "category",
        "All"
    )

    connection = get_db_connection()

    if category == "All":

        foods = connection.execute(
            """
            SELECT *
            FROM foods
            WHERE available = 1
            ORDER BY id DESC
            """
        ).fetchall()

    else:

        foods = connection.execute(
            """
            SELECT *
            FROM foods
            WHERE available = 1
            AND category = ?
            ORDER BY id DESC
            """,
            (category,)
        ).fetchall()

    categories = connection.execute(
        """
        SELECT DISTINCT category
        FROM foods
        WHERE available = 1
        ORDER BY category
        """
    ).fetchall()

    cart_count = connection.execute(
        """
        SELECT COALESCE(SUM(quantity), 0) AS count
        FROM cart
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()["count"]

    connection.close()

    return render_template(
        "menu.html",
        foods=foods,
        categories=categories,
        selected_category=category,
        cart_count=cart_count
    )


# =========================================================
# ADD TO CART
# =========================================================

@app.route("/add-to-cart/<int:food_id>", methods=["POST"])
def add_to_cart(food_id):

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    quantity = request.form.get(
        "quantity",
        1
    )

    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1

    if quantity < 1:
        quantity = 1

    connection = get_db_connection()

    food = connection.execute(
        """
        SELECT *
        FROM foods
        WHERE id = ? AND available = 1
        """,
        (food_id,)
    ).fetchone()

    if food is None:
        connection.close()
        flash("Food item is not available.")
        return redirect(url_for("menu"))

    existing_item = connection.execute(
        """
        SELECT *
        FROM cart
        WHERE user_id = ? AND food_id = ?
        """,
        (
            session["user_id"],
            food_id
        )
    ).fetchone()

    if existing_item:

        connection.execute(
            """
            UPDATE cart
            SET quantity = quantity + ?
            WHERE user_id = ? AND food_id = ?
            """,
            (
                quantity,
                session["user_id"],
                food_id
            )
        )

    else:

        connection.execute(
            """
            INSERT INTO cart
            (
                user_id,
                food_id,
                quantity
            )
            VALUES (?, ?, ?)
            """,
            (
                session["user_id"],
                food_id,
                quantity
            )
        )

    connection.commit()
    connection.close()

    flash(
        f"{food['name']} added to cart."
    )

    return redirect(
        request.referrer or url_for("menu")
    )


# =========================================================
# CART
# =========================================================

@app.route("/cart")
def cart():

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    connection = get_db_connection()

    cart_items = connection.execute(
        """
        SELECT
            cart.id,
            cart.food_id,
            cart.quantity,
            foods.name,
            foods.description,
            foods.price,
            foods.category
        FROM cart
        JOIN foods
            ON cart.food_id = foods.id
        WHERE cart.user_id = ?
        ORDER BY cart.id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    total = sum(
        item["price"] * item["quantity"]
        for item in cart_items
    )

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )


# =========================================================
# UPDATE CART
# =========================================================

@app.route("/update-cart/<int:cart_id>", methods=["POST"])
def update_cart(cart_id):

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    try:
        quantity = int(
            request.form.get(
                "quantity",
                1
            )
        )
    except ValueError:
        quantity = 1

    connection = get_db_connection()

    if quantity <= 0:

        connection.execute(
            """
            DELETE FROM cart
            WHERE id = ? AND user_id = ?
            """,
            (
                cart_id,
                session["user_id"]
            )
        )

    else:

        connection.execute(
            """
            UPDATE cart
            SET quantity = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                quantity,
                cart_id,
                session["user_id"]
            )
        )

    connection.commit()
    connection.close()

    return redirect(url_for("cart"))


# =========================================================
# REMOVE FROM CART
# =========================================================

@app.route("/remove-from-cart/<int:cart_id>", methods=["POST"])
def remove_from_cart(cart_id):

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM cart
        WHERE id = ? AND user_id = ?
        """,
        (
            cart_id,
            session["user_id"]
        )
    )

    connection.commit()
    connection.close()

    flash("Item removed from cart.")

    return redirect(url_for("cart"))


# =========================================================
# CHECKOUT
# =========================================================

@app.route("/checkout")
def checkout():

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    connection = get_db_connection()

    cart_items = connection.execute(
        """
        SELECT
            cart.food_id,
            cart.quantity,
            foods.name,
            foods.price
        FROM cart
        JOIN foods
            ON cart.food_id = foods.id
        WHERE cart.user_id = ?
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    if not cart_items:
        flash("Your cart is empty.")
        return redirect(url_for("menu"))

    total = sum(
        item["price"] * item["quantity"]
        for item in cart_items
    )

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total=total
    )


# =========================================================
# PROCESS PAYMENT
# =========================================================

@app.route("/process-payment", methods=["POST"])
def process_payment():

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    payment_method = request.form.get(
        "payment_method",
        ""
    ).strip()

    if payment_method not in [
        "UPI",
        "Cash"
    ]:
        flash("Please select a valid payment method.")
        return redirect(url_for("checkout"))

    connection = get_db_connection()

    cart_items = connection.execute(
        """
        SELECT
            cart.food_id,
            cart.quantity,
            foods.name,
            foods.price
        FROM cart
        JOIN foods
            ON cart.food_id = foods.id
        WHERE cart.user_id = ?
        """,
        (session["user_id"],)
    ).fetchall()

    if not cart_items:
        connection.close()
        flash("Your cart is empty.")
        return redirect(url_for("cart"))

    total_amount = sum(
        item["price"] * item["quantity"]
        for item in cart_items
    )

    # -----------------------------------------------------
    # ONLINE PAYMENT
    # -----------------------------------------------------

    if payment_method == "UPI":

        connection.close()

        return render_template(
            "online_payment.html",
            total=total_amount
        )

    # -----------------------------------------------------
    # CASH PAYMENT
    # -----------------------------------------------------

    cursor = connection.execute(
        """
        INSERT INTO orders
        (
            user_id,
            total_amount,
            status
        )
        VALUES (?, ?, ?)
        """,
        (
            session["user_id"],
            total_amount,
            "Placed"
        )
    )

    order_id = cursor.lastrowid

    for item in cart_items:

        connection.execute(
            """
            INSERT INTO order_items
            (
                order_id,
                food_id,
                food_name,
                price,
                quantity
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                order_id,
                item["food_id"],
                item["name"],
                item["price"],
                item["quantity"]
            )
        )

    # Cash payment remains Pending
    connection.execute(
        """
        INSERT INTO payments
        (
            order_id,
            payment_method,
            transaction_id,
            amount,
            payment_status,
            payment_date
        )
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (
            order_id,
            "Cash",
            None,
            total_amount,
            "Pending"
        )
    )

    # Clear cart
    connection.execute(
        """
        DELETE FROM cart
        WHERE user_id = ?
        """,
        (session["user_id"],)
    )

    connection.commit()
    connection.close()

    flash(
        f"Order #{order_id} placed successfully. "
        "Please pay at the counter."
    )

    return redirect(
        url_for(
            "order_details",
            order_id=order_id
        )
    )


# =========================================================
# COMPLETE ONLINE PAYMENT
# =========================================================

@app.route("/complete-online-payment", methods=["POST"])
def complete_online_payment():

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    transaction_id = request.form.get(
        "transaction_id",
        ""
    ).strip()

    if not transaction_id:
        flash("Please enter your UPI transaction ID.")
        return redirect(url_for("checkout"))

    connection = get_db_connection()

    cart_items = connection.execute(
        """
        SELECT
            cart.food_id,
            cart.quantity,
            foods.name,
            foods.price
        FROM cart
        JOIN foods
            ON cart.food_id = foods.id
        WHERE cart.user_id = ?
        """,
        (session["user_id"],)
    ).fetchall()

    if not cart_items:
        connection.close()
        flash("Your cart is empty.")
        return redirect(url_for("cart"))

    total_amount = sum(
        item["price"] * item["quantity"]
        for item in cart_items
    )

    # Create order
    cursor = connection.execute(
        """
        INSERT INTO orders
        (
            user_id,
            total_amount,
            status
        )
        VALUES (?, ?, ?)
        """,
        (
            session["user_id"],
            total_amount,
            "Placed"
        )
    )

    order_id = cursor.lastrowid

    # Create order items
    for item in cart_items:

        connection.execute(
            """
            INSERT INTO order_items
            (
                order_id,
                food_id,
                food_name,
                price,
                quantity
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                order_id,
                item["food_id"],
                item["name"],
                item["price"],
                item["quantity"]
            )
        )

    # Online payment = Paid
    connection.execute(
        """
        INSERT INTO payments
        (
            order_id,
            payment_method,
            transaction_id,
            amount,
            payment_status,
            payment_date
        )
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (
            order_id,
            "UPI",
            transaction_id,
            total_amount,
            "Paid"
        )
    )

    # Clear cart
    connection.execute(
        """
        DELETE FROM cart
        WHERE user_id = ?
        """,
        (session["user_id"],)
    )

    connection.commit()
    connection.close()

    flash(
        f"Payment successful! "
        f"Order #{order_id} has been placed."
    )

    return redirect(
        url_for(
            "order_details",
            order_id=order_id
        )
    )


# =========================================================
# USER ORDERS
# =========================================================

@app.route("/my-orders")
def my_orders():

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    connection = get_db_connection()

    orders = connection.execute(
        """
        SELECT
            orders.id,
            orders.total_amount,
            orders.status,
            orders.order_date,
            payments.payment_method,
            payments.payment_status
        FROM orders
        LEFT JOIN payments
            ON orders.id = payments.order_id
        WHERE orders.user_id = ?
        ORDER BY orders.id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "my_orders.html",
        orders=orders
    )


# =========================================================
# USER ORDER DETAILS
# =========================================================

@app.route("/order/<int:order_id>")
def order_details(order_id):

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    connection = get_db_connection()

    order = connection.execute(
        """
        SELECT *
        FROM orders
        WHERE id = ?
        AND user_id = ?
        """,
        (
            order_id,
            session["user_id"]
        )
    ).fetchone()

    if order is None:
        connection.close()
        flash("Order not found.")
        return redirect(url_for("my_orders"))

    items = connection.execute(
        """
        SELECT *
        FROM order_items
        WHERE order_id = ?
        ORDER BY id
        """,
        (order_id,)
    ).fetchall()

    payment = connection.execute(
        """
        SELECT *
        FROM payments
        WHERE order_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (order_id,)
    ).fetchone()

    connection.close()

    return render_template(
        "order_details.html",
        order=order,
        items=items,
        payment=payment
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    connection = get_db_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    connection.close()

    if user is None:
        session.clear()
        flash("User account not found.")
        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        user=user
    )


# =========================================================
# UPDATE PROFILE
# =========================================================

@app.route("/update-profile", methods=["POST"])
def update_profile():

    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    full_name = request.form.get(
        "full_name",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    if not full_name or not phone or not email:
        flash("Please fill in all fields.")
        return redirect(url_for("profile"))

    connection = get_db_connection()

    existing_email = connection.execute(
        """
        SELECT id
        FROM users
        WHERE email = ?
        AND id != ?
        """,
        (
            email,
            session["user_id"]
        )
    ).fetchone()

    if existing_email:
        connection.close()
        flash("Email already belongs to another account.")
        return redirect(url_for("profile"))

    connection.execute(
        """
        UPDATE users
        SET full_name = ?,
            phone = ?,
            email = ?
        WHERE id = ?
        """,
        (
            full_name,
            phone,
            email,
            session["user_id"]
        )
    )

    connection.commit()
    connection.close()

    session["full_name"] = full_name
    session["email"] = email

    flash("Profile updated successfully.")

    return redirect(url_for("profile"))


# =========================================================
# ADMIN AUTH CHECK
# =========================================================

def admin_required():

    if "user_id" not in session:
        return False

    if session.get("role") != "admin":
        return False

    return True


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin-dashboard")
def admin_dashboard():

    if not admin_required():
        return redirect(url_for("login"))

    connection = get_db_connection()

    total_foods = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM foods
        """
    ).fetchone()["count"]

    total_users = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM users
        WHERE role = 'user'
        """
    ).fetchone()["count"]

    total_orders = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM orders
        """
    ).fetchone()["count"]

    total_sales = connection.execute(
        """
        SELECT COALESCE(SUM(total_amount), 0) AS total
        FROM orders
        WHERE status != 'Cancelled'
        """
    ).fetchone()["total"]

    recent_orders = connection.execute(
        """
        SELECT
            orders.id,
            orders.total_amount,
            orders.status,
            orders.order_date,
            users.full_name
        FROM orders
        JOIN users
            ON orders.user_id = users.id
        ORDER BY orders.id DESC
        LIMIT 5
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin_dashboard.html",
        total_foods=total_foods,
        total_users=total_users,
        total_orders=total_orders,
        total_sales=total_sales,
        total_revenue=total_sales,
        recent_orders=recent_orders
    )


# =========================================================
# ADMIN FOOD
# =========================================================

@app.route("/admin-food")
def admin_food():

    if not admin_required():
        return redirect(url_for("login"))

    connection = get_db_connection()

    foods = connection.execute(
        """
        SELECT *
        FROM foods
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin_food.html",
        foods=foods
    )


# =========================================================
# ADMIN ADD FOOD
# =========================================================

@app.route("/admin-food/add", methods=["GET", "POST"])
def admin_add_food():

    if not admin_required():
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        price = request.form.get(
            "price",
            ""
        ).strip()

        available = request.form.get(
            "available"
        )

        if not name or not category or not price:
            flash("Please fill in all required fields.")
            return redirect(url_for("admin_add_food"))

        try:
            price = float(price)
        except ValueError:
            flash("Invalid price.")
            return redirect(url_for("admin_add_food"))

        available_value = 1 if available else 0

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO foods
            (
                name,
                description,
                price,
                category,
                available
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                description,
                price,
                category,
                available_value
            )
        )

        connection.commit()
        connection.close()

        flash("Food item added successfully.")

        return redirect(url_for("admin_food"))

    return render_template("admin_add_food.html")


# =========================================================
# ADMIN EDIT FOOD
# =========================================================

@app.route(
    "/admin-food/edit/<int:food_id>",
    methods=["GET", "POST"]
)
def admin_edit_food(food_id):

    if not admin_required():
        return redirect(url_for("login"))

    connection = get_db_connection()

    food = connection.execute(
        """
        SELECT *
        FROM foods
        WHERE id = ?
        """,
        (food_id,)
    ).fetchone()

    if food is None:
        connection.close()
        flash("Food item not found.")
        return redirect(url_for("admin_food"))

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        price = request.form.get(
            "price",
            ""
        ).strip()

        available = request.form.get(
            "available"
        )

        if not name or not category or not price:
            connection.close()
            flash("Please fill in all required fields.")
            return redirect(
                url_for(
                    "admin_edit_food",
                    food_id=food_id
                )
            )

        try:
            price = float(price)
        except ValueError:
            connection.close()
            flash("Invalid price.")
            return redirect(
                url_for(
                    "admin_edit_food",
                    food_id=food_id
                )
            )

        available_value = 1 if available else 0

        connection.execute(
            """
            UPDATE foods
            SET name = ?,
                description = ?,
                price = ?,
                category = ?,
                available = ?
            WHERE id = ?
            """,
            (
                name,
                description,
                price,
                category,
                available_value,
                food_id
            )
        )

        connection.commit()
        connection.close()

        flash("Food item updated successfully.")

        return redirect(url_for("admin_food"))

    connection.close()

    return render_template(
        "admin_edit_food.html",
        food=food
    )


# =========================================================
# DELETE FOOD
# =========================================================

@app.route(
    "/admin-food/delete/<int:food_id>",
    methods=["POST"]
)
def admin_delete_food(food_id):

    if not admin_required():
        return redirect(url_for("login"))

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM foods
        WHERE id = ?
        """,
        (food_id,)
    )

    connection.commit()
    connection.close()

    flash("Food item deleted.")

    return redirect(url_for("admin_food"))


# =========================================================
# ADMIN ORDERS
# =========================================================

@app.route("/admin-orders")
def admin_orders():

    if not admin_required():
        return redirect(url_for("login"))

    connection = get_db_connection()

    orders = connection.execute(
        """
        SELECT
            orders.id,
            orders.total_amount,
            orders.status,
            orders.order_date,

            users.full_name,
            users.email,
            users.student_id,

            payments.payment_method,
            payments.payment_status,
            payments.transaction_id

        FROM orders

        JOIN users
            ON orders.user_id = users.id

        LEFT JOIN payments
            ON orders.id = payments.order_id

        ORDER BY orders.id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin_orders.html",
        orders=orders
    )


# =========================================================
# ADMIN ORDER DETAILS
# =========================================================

@app.route(
    "/admin-order-details/<int:order_id>"
)
def admin_order_details(order_id):

    if not admin_required():
        return redirect(url_for("login"))

    connection = get_db_connection()

    order = connection.execute(
        """
        SELECT
            orders.*,
            users.full_name,
            users.email,
            users.student_id,
            users.phone
        FROM orders
        JOIN users
            ON orders.user_id = users.id
        WHERE orders.id = ?
        """,
        (order_id,)
    ).fetchone()

    if order is None:
        connection.close()
        flash("Order not found.")
        return redirect(url_for("admin_orders"))

    items = connection.execute(
        """
        SELECT *
        FROM order_items
        WHERE order_id = ?
        ORDER BY id
        """,
        (order_id,)
    ).fetchall()

    payment = connection.execute(
        """
        SELECT *
        FROM payments
        WHERE order_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (order_id,)
    ).fetchone()

    connection.close()

    return render_template(
        "admin_order_details.html",
        order=order,
        items=items,
        payment=payment
    )


# =========================================================
# ADMIN UPDATE ORDER STATUS
# =========================================================

@app.route(
    "/admin-update-order-status/<int:order_id>",
    methods=["POST"]
)
def admin_update_order_status(order_id):

    if not admin_required():
        return redirect(url_for("login"))

    status = request.form.get(
        "status",
        ""
    ).strip()

    allowed_statuses = [
        "Placed",
        "Preparing",
        "Ready",
        "Completed",
        "Cancelled"
    ]

    if status not in allowed_statuses:
        flash("Invalid order status.")
        return redirect(
            url_for(
                "admin_order_details",
                order_id=order_id
            )
        )

    connection = get_db_connection()

    connection.execute(
        """
        UPDATE orders
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            order_id
        )
    )

    connection.commit()
    connection.close()

    flash("Order status updated successfully.")

    return redirect(
        url_for(
            "admin_order_details",
            order_id=order_id
        )
    )


# =========================================================
# ADMIN MARK CASH PAYMENT AS PAID
# =========================================================

@app.route(
    "/admin/payment/<int:order_id>/mark-paid",
    methods=["POST"]
)
def admin_mark_payment_paid(order_id):

    if not admin_required():
        return redirect(url_for("login"))

    connection = get_db_connection()

    payment = connection.execute(
        """
        SELECT *
        FROM payments
        WHERE order_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (order_id,)
    ).fetchone()

    if payment is None:
        connection.close()
        flash("Payment record not found.")
        return redirect(
            url_for(
                "admin_order_details",
                order_id=order_id
            )
        )

    connection.execute(
        """
        UPDATE payments
        SET payment_status = ?,
            payment_date = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            "Paid",
            payment["id"]
        )
    )

    connection.commit()
    connection.close()

    flash("Payment marked as Paid.")

    return redirect(
        url_for(
            "admin_order_details",
            order_id=order_id
        )
    )


# =========================================================
# ADMIN USERS
# =========================================================

@app.route("/admin-users")
def admin_users():

    if not admin_required():
        return redirect(url_for("login"))

    connection = get_db_connection()

    users = connection.execute(
        """
        SELECT
            id,
            full_name,
            student_id,
            email,
            phone,
            role
        FROM users
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin_users.html",
        users=users
    )


# =========================================================
# DELETE USER
# =========================================================

@app.route(
    "/admin-users/delete/<int:user_id>",
    methods=["POST"]
)
def admin_delete_user(user_id):

    if not admin_required():
        return redirect(url_for("login"))

    # Prevent admin from deleting their own account
    if user_id == session["user_id"]:
        flash("You cannot delete your own admin account.")
        return redirect(url_for("admin_users"))

    connection = get_db_connection()

    # Remove user's cart
    connection.execute(
        """
        DELETE FROM cart
        WHERE user_id = ?
        """,
        (user_id,)
    )

    # Remove user's orders and related records
    orders = connection.execute(
        """
        SELECT id
        FROM orders
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchall()

    for order in orders:

        connection.execute(
            """
            DELETE FROM payments
            WHERE order_id = ?
            """,
            (order["id"],)
        )

        connection.execute(
            """
            DELETE FROM order_items
            WHERE order_id = ?
            """,
            (order["id"],)
        )

    connection.execute(
        """
        DELETE FROM orders
        WHERE user_id = ?
        """,
        (user_id,)
    )

    connection.execute(
        """
        DELETE FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    connection.commit()
    connection.close()

    flash("User deleted successfully.")

    return redirect(url_for("admin_users"))


# =========================================================
# SALES ANALYTICS
# =========================================================

@app.route("/sales-analytics")
def sales_analytics():

    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/")

    connection = get_db_connection()

    # -----------------------------------------------------
    # TOTAL SALES
    # -----------------------------------------------------

    result = connection.execute(
        """
        SELECT COALESCE(SUM(total_amount), 0) AS total_sales
        FROM orders
        WHERE status != 'Cancelled'
        """
    ).fetchone()

    total_sales = result["total_sales"]

    # -----------------------------------------------------
    # TOTAL ORDERS
    # -----------------------------------------------------

    result = connection.execute(
        """
        SELECT COUNT(*) AS total_orders
        FROM orders
        WHERE status != 'Cancelled'
        """
    ).fetchone()

    total_orders = result["total_orders"]

    # -----------------------------------------------------
    # AVERAGE ORDER
    # -----------------------------------------------------

    if total_orders > 0:
        average_order = total_sales / total_orders
    else:
        average_order = 0

    # -----------------------------------------------------
    # TODAY'S SALES
    # -----------------------------------------------------

    result = connection.execute(
        """
        SELECT COALESCE(SUM(total_amount), 0) AS today_sales
        FROM orders
        WHERE DATE(order_date) = DATE('now')
        AND status != 'Cancelled'
        """
    ).fetchone()

    today_sales = result["today_sales"]

    # -----------------------------------------------------
    # TODAY'S ORDERS
    # -----------------------------------------------------

    result = connection.execute(
        """
        SELECT COUNT(*) AS today_orders
        FROM orders
        WHERE DATE(order_date) = DATE('now')
        AND status != 'Cancelled'
        """
    ).fetchone()

    today_orders = result["today_orders"]

    # -----------------------------------------------------
    # DAILY SALES FOR CHART
    # -----------------------------------------------------

    daily_sales = connection.execute(
        """
        SELECT
            DATE(order_date) AS sale_date,
            COUNT(*) AS order_count,
            COALESCE(SUM(total_amount), 0) AS sales
        FROM orders
        WHERE status != 'Cancelled'
        GROUP BY DATE(order_date)
        ORDER BY sale_date DESC
        LIMIT 7
        """
    ).fetchall()

    # -----------------------------------------------------
    # CATEGORY SALES
    # -----------------------------------------------------

    category_sales = connection.execute(
        """
        SELECT
            foods.category,
            COALESCE(
                SUM(
                    order_items.price *
                    order_items.quantity
                ),
                0
            ) AS sales
        FROM order_items
        JOIN foods
            ON order_items.food_id = foods.id
        JOIN orders
            ON order_items.order_id = orders.id
        WHERE orders.status != 'Cancelled'
        GROUP BY foods.category
        ORDER BY sales DESC
        """
    ).fetchall()

    # -----------------------------------------------------
    # TOP FOODS
    # -----------------------------------------------------

    top_foods = connection.execute(
        """
        SELECT
            order_items.food_name,
            SUM(order_items.quantity) AS quantity_sold,
            COALESCE(
                SUM(
                    order_items.price *
                    order_items.quantity
                ),
                0
            ) AS revenue
        FROM order_items
        JOIN orders
            ON order_items.order_id = orders.id
        WHERE orders.status != 'Cancelled'
        GROUP BY
            order_items.food_id,
            order_items.food_name
        ORDER BY quantity_sold DESC
        LIMIT 10
        """
    ).fetchall()

    # -----------------------------------------------------
    # PAYMENT SUMMARY
    # -----------------------------------------------------

    payment_summary = connection.execute(
        """
        SELECT
            payments.payment_method,
            COUNT(*) AS payment_count,
            COALESCE(
                SUM(payments.amount),
                0
            ) AS payment_total
        FROM payments
        JOIN orders
            ON payments.order_id = orders.id
        WHERE orders.status != 'Cancelled'
        GROUP BY payments.payment_method
        """
    ).fetchall()

    connection.close()

    return render_template(
        "sales_analytics.html",
        total_sales=total_sales,
        total_orders=total_orders,
        average_order=average_order,
        today_sales=today_sales,
        today_orders=today_orders,
        daily_sales=daily_sales,
        category_sales=category_sales,
        top_foods=top_foods,
        payment_summary=payment_summary
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )