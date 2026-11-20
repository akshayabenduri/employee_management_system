"""
Create (or reset) the administrator account with a HASHED password.
Run once after creating the database:   python create_admin.py
"""
import getpass
import mysql.connector
from werkzeug.security import generate_password_hash
from app.db import run_query

username = input("Admin username [admin]: ").strip() or "admin"
password = getpass.getpass("Admin password (min 6 chars): ")

if len(password) < 6:
    raise SystemExit("Password is too short. Please use at least 6 characters.")

try:
    hashed = generate_password_hash(password)
    run_query(
        "INSERT INTO admins (username, password_hash) VALUES (%s, %s) "
        "ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash)",
        (username, hashed), fetch=None, commit=True)
    print(f"Admin '{username}' is ready. You can log in now.")
except mysql.connector.Error as err:
    raise SystemExit(f"Database error: {err}")
