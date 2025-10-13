import sqlite3
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

DB = "users.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_name   TEXT NOT NULL,
  user_email  TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at  TEXT NOT NULL
);
"""

def create_db():
    with sqlite3.connect(DB) as conn:
        conn.execute(SCHEMA)
        conn.commit()

def add_user(user_name: str, user_email: str, password: str):
    user_email = user_email.strip().lower()
    pwd_hash = generate_password_hash(password)
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT INTO user (user_name, user_email, password_hash, created_at) VALUES (?,?,?,?)",
            (user_name, user_email, pwd_hash, now),
        )
        conn.commit()

def verify_user(user_email: str, password: str) -> bool:
    user_email = user_email.strip().lower()
    with sqlite3.connect(DB) as conn:
        row = conn.execute(
            "SELECT password_hash FROM user WHERE user_email=?",
            (user_email,)
        ).fetchone()
    return bool(row and check_password_hash(row[0], password))

if __name__ == "__main__":
    create_db()
    # demo insert
    add_user("Alice", "alice@example.com", "s3cure-pass")
    print("Verify:", verify_user("alice@example.com", "s3cure-pass"))
