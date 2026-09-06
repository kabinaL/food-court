from werkzeug.security import generate_password_hash
from database import get_db_connection

email = "nava@gmail.com"
new_password = "nava123"

hashed_password = generate_password_hash(new_password)

connection = get_db_connection()

connection.execute("""
    UPDATE users
    SET password = ?
    WHERE email = ?
""", (
    hashed_password,
    email
))

connection.commit()

user = connection.execute("""
    SELECT id, full_name, email, role
    FROM users
    WHERE email = ?
""", (email,)).fetchone()

connection.close()

if user:
    print("Password reset successfully!")
    print("Name:", user["full_name"])
    print("Email:", user["email"])
    print("Role:", user["role"])
    print("New password:", new_password)
else:
    print("User not found.")