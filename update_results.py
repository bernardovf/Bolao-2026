import requests
import psycopg2
import os


DATABASE_URL = os.environ.get('DATABASE_URL')
API_KEY = os.environ.get('API_KEY')

headers = {"X-Auth-Token": API_KEY}

if DATABASE_URL:
    print("Connecting to PostgreSQL (production)...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

url = "https://api.football-data.org/v4/competitions/2000/matches"
response = requests.get(url, headers=headers)
matches = response.json()["matches"]
matches_by_id = {
    m["id"]: m
    for m in matches
    if m["status"] == "FINISHED"
}

cur.execute("""
    SELECT id
    FROM fixtures
    WHERE final_home_goals IS NULL
      AND final_away_goals IS NULL
""")

fixture_ids = [row[0] for row in cur.fetchall()]
updated = 0

for match_id in fixture_ids:
    print(match_id)
    if match_id not in matches_by_id:
        continue
    m = matches_by_id[match_id]

    if m["status"] == "FINISHED":
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]
        home_goals = m["score"]["fullTime"]["home"]
        away_goals = m["score"]["fullTime"]["away"]
        print(home, away)

        cur.execute("""
            UPDATE fixtures
            SET
                final_home_goals = %s,
                final_away_goals = %s
            WHERE id = %s
        """, (home_goals, away_goals, match_id))

        updated += 1

conn.commit()
cur.close()
conn.close()

print(f"Checked {len(fixture_ids)} fixtures. Updated {updated}.")