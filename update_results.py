import requests
import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
API_KEY = os.environ.get("API_KEY")

# API-Football / API-Sports
headers = {"x-apisports-key": API_KEY}

# API-Football fixture_id -> your old football-data.org fixture id
FIXTURE_ID_MAP = {
    1489369: 537327,
    1538999: 537328,
    1539004: 537329,
    1489388: 537330,
    1539010: 537331,
    1489407: 537332,
    1539000: 537333,
    1489373: 537334,
    1539005: 537335,
    1489387: 537336,
    1489408: 537337,
    1539009: 537338,
    1489371: 537339,
    1489372: 537340,
    1489389: 537341,
    1489390: 537342,
    1489405: 537343,
    1489406: 537344,
    1489370: 537345,
    1539001: 537346,
    1539006: 537347,
    1489391: 537348,
    1539012: 537349,
    1489411: 537350,
    1489374: 537351,
    1489375: 537352,
    1489393: 537353,
    1489392: 537354,
    1489410: 537355,
    1489409: 537356,
    1489376: 537357,
    1539002: 537358,
    1539007: 537359,
    1489394: 537360,
    1489412: 537361,
    1539011: 537362,
    1489377: 537363,
    1489378: 537364,
    1489395: 537365,
    1489396: 537366,
    1489415: 537367,
    1489414: 537368,
    1489380: 537369,
    1489379: 537370,
    1489397: 537371,
    1489398: 537372,
    1489417: 537373,
    1489413: 537374,
    1489383: 537391,
    1539016: 537392,
    1539017: 537393,
    1489401: 537394,
    1489416: 537395,
    1539074: 537396,
    1489381: 537397,
    1489382: 537398,
    1489399: 537399,
    1489400: 537400,
    1489418: 537401,
    1489421: 537402,
    1539003: 537403,
    1489386: 537404,
    1489404: 537405,
    1539008: 537406,
    1489419: 537407,
    1539013: 537408,
    1489384: 537409,
    1489385: 537410,
    1489402: 537411,
    1489403: 537412,
    1489422: 537413,
    1489420: 537414,
}

TEAM_MAP = {
    "Mexico": "Mexico",
    "South Korea": "Korea Republic",
    "Czechia": "Czech Republic",
    "South Africa": "South Africa",
    "Canada": "Canada",
    "Qatar": "Qatar",
    "Switzerland": "Switzerland",
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
    "Brazil": "Brazil",
    "Haiti": "Haiti",
    "Scotland": "Scotland",
    "Morocco": "Morocco",
    "USA": "USA",
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
    url = "https://v3.football.api-sports.io/fixtures"

    # API-Football supports ids as a joined string
    # If this ever fails due to too many ids, split into chunks of 20.
    ids_param = "-".join(str(x) for x in api_fixture_ids)

    response = requests.get(
        url,
        headers=headers,
        params=params
    )
    response.raise_for_status()

    data = response.json()
    fixtures = data.get("response", [])

    for item in fixtures:
        api_fixture_id = item["fixture"]["id"]
        old_match_id = FIXTURE_ID_MAP.get(api_fixture_id)

        if old_match_id is None:
            continue

        status = item["fixture"]["status"]["short"]

        # API-Football finished status is usually FT
        # AET/PEN can happen in knockout phase, but group stage should be FT.
        if status == "NS":
            continue

        home_goals = item["goals"]["home"]
        away_goals = item["goals"]["away"]

        if home_goals is None or away_goals is None:
            continue

        home = item["teams"]["home"]["name"]
        away = item["teams"]["away"]["name"]

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