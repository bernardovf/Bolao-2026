#!/usr/bin/env python3
"""Populate database with test users, bets, and match results."""

import sqlite3
import random
from datetime import datetime

# Connect to database
conn = sqlite3.connect('bolao_2026_dev.db')
cursor = conn.cursor()

# 10 Brazilian names for users
users_data = [
    ('João Silva', 'senha123'),
    ('Maria Santos', 'senha123'),
    ('Pedro Oliveira', 'senha123'),
    ('Ana Costa', 'senha123'),
    ('Carlos Souza', 'senha123'),
    ('Juliana Lima', 'senha123'),
    ('Ricardo Alves', 'senha123'),
    ('Fernanda Rocha', 'senha123'),
    ('Lucas Martins', 'senha123'),
    ('Beatriz Pereira', 'senha123'),
]

print("🔧 Setting up database schema...")
# Add final score columns to fixtures table if they don't exist
try:
    cursor.execute("ALTER TABLE fixtures ADD COLUMN final_home_goals INTEGER")
    cursor.execute("ALTER TABLE fixtures ADD COLUMN final_away_goals INTEGER")
    print("  ✓ Added final score columns to fixtures table")
except sqlite3.OperationalError:
    print("  ✓ Final score columns already exist in fixtures table")
conn.commit()

print("\n🔄 Cleaning existing test data...")
# Delete existing users (keep id 1 which might be the admin)
cursor.execute("DELETE FROM users WHERE id > 1")
cursor.execute("DELETE FROM bet WHERE user_id > 1")
conn.commit()

print("👥 Creating 10 users...")
user_ids = []
for name, password in users_data:
    cursor.execute(
        "INSERT INTO users (user_name, password) VALUES (?, ?)",
        (name, password)
    )
    user_ids.append(cursor.lastrowid)
    print(f"  ✓ Created user: {name} (ID: {cursor.lastrowid})")

conn.commit()

# Get all group stage matches
print("\n⚽ Fetching group stage matches...")
cursor.execute("SELECT id, home, away, phase FROM fixtures WHERE phase LIKE 'Group%' ORDER BY id LIMIT 48")
fixtures = cursor.fetchall()
print(f"  Found {len(fixtures)} group stage matches")

# Real World Cup 2026 style results (varied and realistic)
print("\n📊 Adding realistic bets for all users...")

bet_count = 0
for user_id in user_ids:
    user_name = users_data[user_id - 2][0]  # Adjust index

    for match_id, home, away, phase in fixtures:
        # Create varied betting patterns
        # Some users are optimistic (high scores), some conservative (low scores)
        user_style = user_id % 3

        if user_style == 0:  # Conservative better
            home_goals = random.choice([0, 0, 1, 1, 1, 2])
            away_goals = random.choice([0, 0, 1, 1, 1, 2])
        elif user_style == 1:  # Balanced better
            home_goals = random.choice([0, 1, 1, 2, 2, 3])
            away_goals = random.choice([0, 1, 1, 2, 2, 3])
        else:  # Optimistic better (high scores)
            home_goals = random.choice([1, 2, 2, 3, 3, 4])
            away_goals = random.choice([0, 1, 2, 2, 3, 3])

        try:
            cursor.execute(
                "INSERT INTO bet (user_id, match_id, home_goals, away_goals) VALUES (?, ?, ?, ?)",
                (user_id, match_id, home_goals, away_goals)
            )
            bet_count += 1
        except sqlite3.IntegrityError:
            pass  # Bet already exists

conn.commit()
print(f"  ✓ Created {bet_count} bets")

# Add real results to some matches
print("\n🎯 Adding real match results...")
results = [
    # Match_id will be dynamically assigned based on actual fixtures
    # Format: (home_goals, away_goals) - varied realistic results
    (2, 1), (1, 1), (3, 0), (1, 0), (2, 2),
    (0, 0), (2, 1), (1, 2), (3, 1), (0, 1),
    (2, 0), (1, 1), (4, 2), (2, 1), (1, 0),
    (0, 2), (3, 3), (1, 0), (2, 1), (1, 1),
]

result_count = 0
for idx, (match_id, home, away, phase) in enumerate(fixtures[:20]):  # Add results to first 20 matches
    if idx < len(results):
        home_goals, away_goals = results[idx]
        cursor.execute(
            "UPDATE fixtures SET final_home_goals = ?, final_away_goals = ? WHERE id = ?",
            (home_goals, away_goals, match_id)
        )
        result_count += 1
        print(f"  ✓ {home} {home_goals} x {away_goals} {away} (Match ID: {match_id})")

conn.commit()
print(f"\n✓ Added {result_count} match results")

# Show ranking preview
print("\n📊 Calculating rankings...")
cursor.execute("""
    SELECT
        u.user_name,
        COUNT(CASE WHEN b.home_goals = f.final_home_goals
                    AND b.away_goals = f.final_away_goals THEN 1 END) as exact_matches,
        COUNT(CASE WHEN (b.home_goals > b.away_goals AND f.final_home_goals > f.final_away_goals)
                     OR (b.home_goals < b.away_goals AND f.final_home_goals < f.final_away_goals)
                     OR (b.home_goals = b.away_goals AND f.final_home_goals = f.final_away_goals)
                    THEN 1 END) as result_matches,
        SUM(CASE
            WHEN b.home_goals = f.final_home_goals AND b.away_goals = f.final_away_goals THEN 10
            WHEN (b.home_goals > b.away_goals AND f.final_home_goals > f.final_away_goals)
                 OR (b.home_goals < b.away_goals AND f.final_home_goals < f.final_away_goals)
                 OR (b.home_goals = b.away_goals AND f.final_home_goals = f.final_away_goals)
                THEN 5
            ELSE 0
        END) as total_points
    FROM users u
    JOIN bet b ON u.id = b.user_id
    JOIN fixtures f ON b.match_id = f.id
    WHERE f.final_home_goals IS NOT NULL
    GROUP BY u.id, u.user_name
    ORDER BY total_points DESC, exact_matches DESC
""")

rankings = cursor.fetchall()

print("\n🏆 RANKING PREVIEW:")
print("=" * 70)
print(f"{'Pos':<5} {'Jogador':<25} {'Exatos':<10} {'Parciais':<12} {'Pontos':<10}")
print("=" * 70)

for idx, (name, exact, result, points) in enumerate(rankings, 1):
    print(f"{idx:<5} {name:<25} {exact:<10} {result:<12} {int(points):<10}")

print("=" * 70)

conn.close()

print("\n✅ Database populated successfully!")
print(f"   - {len(user_ids)} users created")
print(f"   - {bet_count} bets added")
print(f"   - {result_count} match results added")
print("\n🌐 You can now view the ranking at: http://localhost:5000/ranking")
