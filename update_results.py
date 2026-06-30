import requests
import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
API_KEY = os.environ.get("API_KEY")
BASE_URL = "https://api.football-data.org/v4"

headers = {
    "X-Auth-Token": API_KEY
}

# API-Football fixture_id -> your old football-data.org fixture id
FIXTURE_ID_MAP = {
    537344: 537343,
    537343: 537344,
    537417: 1,
    537423: 2,
    537415: 3,
    537418: 4,
    537424: 5,
    537416: 6,
    537425: 7,
    537426: 8,
    537422: 9,
    537421: 10,
    537420: 11,
    537419: 12,
    537429: 13,
    537428: 14,
    537427: 15,
    537430: 16
}

TEAM_MAP = {
    "Mexico": "Mexico",
    "South Korea": "Korea Republic",
    "Czechia": "Czech Republic",
    "South Africa": "South Africa",
    "Canada": "Canada",
    "Qatar": "Qatar",
    "Switzerland": "Switzerland",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Brazil": "Brazil",
    "Haiti": "Haiti",
    "Scotland": "Scotland",
    "Morocco": "Morocco",
    "United States": "USA",
    "Australia": "Australia",
    "Türkiye": "Turkey",
    "Paraguay": "Paraguay",
    "Germany": "Germany",
    "Ivory Coast": "Côte d'Ivoire",
    "Ecuador": "Ecuador",
    "Curaçao": "Curaçao",
    "Netherlands": "Netherlands",
    "Sweden": "Sweden",
    "Tunisia": "Tunisia",
    "Japan": "Japan",
    "Belgium": "Belgium",
    "Iran": "Iran",
    "New Zealand": "New Zealand",
    "Egypt": "Egypt",
    "Spain": "Spain",
    "Saudi Arabia": "Saudi Arabia",
    "Uruguay": "Uruguay",
    "Cape Verde Islands": "Cabo Verde",
    "France": "France",
    "Iraq": "Iraq",
    "Norway": "Norway",
    "Senegal": "Senegal",
    "Argentina": "Argentina",
    "Austria": "Austria",
    "Jordan": "Jordan",
    "Algeria": "Algeria",
    "Portugal": "Portugal",
    "Uzbekistan": "Uzbekistan",
    "Colombia": "Colombia",
    "Congo DR": "Democratic Republic of the Congo",
    "England": "England",
    "Ghana": "Ghana",
    "Panama": "Panama",
    "Croatia": "Croatia",
}

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing")

if not API_KEY:
    raise ValueError("API_KEY environment variable is missing")

print("Connecting to PostgreSQL...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Get unfinished fixtures from your DB, using old 537xxx ids
cur.execute("""
    SELECT id
    FROM fixtures
    WHERE phase = '16 Avos Final'
""")

unfinished_old_ids = {row[0] for row in cur.fetchall()}
# Only request API-Football fixtures that map to unfinished DB fixtures
api_fixture_ids = [
    api_id
    for api_id, old_id in FIXTURE_ID_MAP.items()
    if old_id in unfinished_old_ids
]
updated = 0

params = {
    "league": 1,      # you need to confirm World Cup league id in API-Football
    "season": 2026
}

if api_fixture_ids:

    url = f"{BASE_URL}/competitions/WC/matches"


    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    data = response.json()
    fixtures = data['matches']

    for item in fixtures:
        api_fixture_id = item["id"]
        old_match_id = FIXTURE_ID_MAP.get(api_fixture_id, api_fixture_id)
        if old_match_id is None:
            continue

        status = item["status"]

        # API-Football finished status is usually FT
        # AET/PEN can happen in knockout phase, but group stage should be FT.
        if status == "NOT STARTED":
            continue

        if "regularTime" in item["score"]:
            home_goals = item["score"]["regularTime"]["home"]
            away_goals = item["score"]["regularTime"]["away"]
        else:
            home_goals = item["score"]["fullTime"]["home"]
            away_goals = item["score"]["fullTime"]["away"]

        home = item["homeTeam"]["name"]
        away = item["awayTeam"]["name"]

        if home_goals is None or away_goals is None:
            print(f"NOT STARTED       {api_fixture_id} -> {old_match_id}: {home} vs {away}")
            continue

        cur.execute("""
            SELECT home, away
            FROM fixtures
            WHERE id = %s
        """, (old_match_id,))

        db_home, db_away = cur.fetchone()

        db_home_norm = TEAM_MAP.get(db_home, db_home)
        home_norm = TEAM_MAP.get(home, home)

        db_away_norm = TEAM_MAP.get(db_away, db_away)
        away_norm = TEAM_MAP.get(away, away)

        same_order = (db_home_norm == home_norm and db_away_norm == away_norm)

        reversed_order = (db_home_norm == away_norm and db_away_norm == home_norm)

        if same_order:
            print(f"OK       {old_match_id}: {db_home} vs {db_away}")

        elif reversed_order:
            print(f"REVERSED {old_match_id}: {db_home} vs {db_away}")

        if same_order:
            db_home_goals = home_goals
            db_away_goals = away_goals

        elif reversed_order:
            db_home_goals = away_goals
            db_away_goals = home_goals

        print(f"Updating {old_match_id}: {db_home_norm} {db_home_goals} - {db_away_norm} {db_away_goals}")

        cur.execute("""
            UPDATE fixtures
            SET
                final_home_goals = %s,
                final_away_goals = %s
            WHERE id = %s
        """, (db_home_goals, db_away_goals, old_match_id))

        updated += 1
        print("")

conn.commit()
cur.close()
conn.close()

print(f"Checked {len(unfinished_old_ids)} unfinished fixtures. Updated {updated}.")