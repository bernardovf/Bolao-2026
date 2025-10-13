import sqlite3
import pandas as pd

DB_PATH = "bolao_2026_dev.db"

# ---------- DB helpers ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
user_name = "Bernardo"
with get_conn() as conn:
    row = conn.execute("SELECT id, user_name, password FROM users WHERE user_name=?", (user_name,)).fetchone()
print(row["password"])
conn.close()
