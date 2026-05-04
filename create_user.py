from werkzeug.security import generate_password_hash
import sqlite3
import psycopg2
import os
import sys

# Get database configuration (same as app)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Get username and password from command line or hardcode them
if len(sys.argv) == 3:
    username = sys.argv[1]
    password = sys.argv[2]
else:
    # Hardcoded values (you can edit these)
    username = "neymar"
    password = "senha123"

# Hash the password
hashed = generate_password_hash(password)

# Connect to appropriate database
if DATABASE_URL:
    # PostgreSQL (production)
    print("Connecting to PostgreSQL (production)...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # PostgreSQL uses %s placeholders
    cur.execute("INSERT INTO users (user_name, password) VALUES (%s, %s)", (username, hashed))

    conn.commit()
    cur.close()
    conn.close()
    print(f"✓ User '{username}' created in PostgreSQL")
else:
    # SQLite (local)
    print("Connecting to SQLite (local)...")
    conn = sqlite3.connect('bolao_2026_dev.db')

    # SQLite uses ? placeholders
    conn.execute("INSERT INTO users (user_name, password) VALUES (?, ?)", (username, hashed))

    conn.commit()
    conn.close()
    print(f"✓ User '{username}' created in SQLite")

print(f"✓ Password: {password}")
print(f"✓ Hash: {hashed[:60]}...")
print(f"\nTell the user: login = {username} / password = {password}")
