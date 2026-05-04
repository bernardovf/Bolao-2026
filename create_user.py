from werkzeug.security import generate_password_hash
import sqlite3
import psycopg2
import os

# Your generated passwords dictionary
passwords = {
    "cetel": "K8v!rT2#Lp9Q",
    "samuel": "Z4@xM7p$Dq1N",
    "paulo": "W9!cB2&hR8tY",
    "botinha": "Q7#nF5z@L2Vm",
    "zeca": "P3$kT8!uXr6A",
    "rafao": "J6&vH1q@N9sC",
    "fabner": "M2!dZ7#yKp5L",
    "motoka": "R8@fW4x$T1nB",
    "kiwi": "U5#cP9!mE2zQ",
    "famato": "D1@vL6&kR8sX",
    "mauity": "T9!bQ3#nJ7wH",
    "rafa castro": "A4$yF8@pC2Lm",
    "naza": "H7!sZ5&uK1rD",
    "gabsi": "E2@xN6#W9vTp",
    "bayao": "C8!qM4$zR1fY",
    "alonso": "B5@tK9!pX3nS",
    "lucas": "G1#rD8&vQ6mZ",
    "rapha motta": "V9!cT2@L5kFp",
    "marinho": "Y3$wH7#nJ1xB",
    "gabriel": "S6@pE2!rM8dQ",
    "impera": "X4#fT9&uK1zA",
    "imperinha": "N8!vC3@qR6mP",
    "calango frito": "L2$hW7#xT9sF",
    "dl": "K5@zR1!pV8qM",
    "michel": "O9#nF4!bT2yX",
    "raphael": "I3@kD8$uC6wZ",
    "fratz": "U7!mQ2#vR9pH",
    "bernardo": "Z1$T5@xF8cK"
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
