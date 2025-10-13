import sqlite3
conn = sqlite3.connect("pickem.db")
cur = conn.cursor()

# See current columns
print(cur.execute("PRAGMA table_info(user);").fetchall())

# 1) Add the column (NULLs allowed)
cur.execute("ALTER TABLE user ADD COLUMN email TEXT;")

# 2) Backfill something (or set emails properly)
# Example demo backfill: name-based placeholder
cur.execute("UPDATE user SET email = lower(name) || '@example.local' WHERE email IS NULL;")

# 3) Create a unique index (enforces uniqueness going forward)
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_user_email ON user(email);")

conn.commit()
conn.close()
