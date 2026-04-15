from werkzeug.security import generate_password_hash
import sqlite3
import psycopg2
import psycopg2.extras
import os

print("Hashing all plain text passwords...\n")

# Get database configuration (same as app)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Connect to appropriate database
if DATABASE_URL:
    # PostgreSQL (production)
    print("Connecting to PostgreSQL (production)...\n")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Get all users where password doesn't look like a hash
    cur.execute(
        "SELECT id, user_name, password FROM users WHERE password NOT LIKE 'pbkdf2:%' AND password NOT LIKE 'scrypt:%'"
    )
    users = cur.fetchall()

    if not users:
        print("No plain text passwords found. All passwords are already hashed!")
        conn.close()
        exit(0)

    print(f"Found {len(users)} user(s) with plain text passwords:\n")

    for user in users:
        old_password = user['password']
        hashed = generate_password_hash(old_password)

        cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, user['id']))

        print(f"✓ {user['user_name']}")
        print(f"  Password: {old_password}")
        print(f"  Hash: {hashed[:60]}...\n")

    conn.commit()
    cur.close()
    conn.close()
else:
    # SQLite (local)
    print("Connecting to SQLite (local)...\n")
    conn = sqlite3.connect('bolao_2026_dev.db')
    conn.row_factory = sqlite3.Row

    # Get all users where password doesn't look like a hash
    users = conn.execute(
        "SELECT id, user_name, password FROM users WHERE password NOT LIKE 'pbkdf2:%' AND password NOT LIKE 'scrypt:%'"
    ).fetchall()

    if not users:
        print("No plain text passwords found. All passwords are already hashed!")
        conn.close()
        exit(0)

    print(f"Found {len(users)} user(s) with plain text passwords:\n")

    for user in users:
        old_password = user['password']
        hashed = generate_password_hash(old_password)

        conn.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user['id']))

        print(f"✓ {user['user_name']}")
        print(f"  Password: {old_password}")
        print(f"  Hash: {hashed[:60]}...\n")

    conn.commit()
    conn.close()

print(f"Done! {len(users)} password(s) hashed successfully.")
print("\nUsers can now log in with their same passwords!")
