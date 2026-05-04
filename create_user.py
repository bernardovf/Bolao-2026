from werkzeug.security import generate_password_hash
import sqlite3
import psycopg2
import os

# Your generated passwords dictionary
passwords = {
    "test": "senha123"
}

# DB config
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

if DATABASE_URL:
    print("Connecting to PostgreSQL (production)...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    for username, password in passwords.items():
        hashed = generate_password_hash(password)

        cur.execute(
            "INSERT INTO users (user_name, password) VALUES (%s, %s)",
            (username, hashed)
        )

        print(f"✓ Created {username} | password: {password}")

    conn.commit()
    cur.close()
    conn.close()

else:
    print("Connecting to SQLite (local)...")
    conn = sqlite3.connect('bolao_2026_dev.db')

    for username, password in passwords.items():
        hashed = generate_password_hash(password)

        conn.execute(
            "INSERT INTO users (user_name, password) VALUES (?, ?)",
            (username, hashed)
        )

        print(f"✓ Created {username} | password: {password}")

    conn.commit()
    conn.close()

print("\nAll users created successfully.")
