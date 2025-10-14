from datetime import datetime
from zoneinfo import ZoneInfo
import sqlite3, os

LOCAL_TZ = os.environ.get("APP_TZ", "America/Sao_Paulo")

TEAM_TO_CODE = {
    "Qatar": "qa",
    "Ecuador": "ec",
    "Senegal": "sn",
    "Netherlands": "nl",
    "England": "gb-eng",
    "Iran": "ir",
    "USA": "us",
    "Wales": "gb-wls",
    "Argentina": "ar",
    "Saudi Arabia": "sa",
    "Mexico": "mx",
    "Poland": "pl",
    "Denmark": "dk",
    "Tunisia": "tn",
    "France": "fr",
    "Australia": "au",
    "Germany": "de",
    "Japan": "jp",
    "Spain": "es",
    "Costa Rica": "cr",
    "Morocco": "ma",
    "Croatia": "hr",
    "Belgium": "be",
    "Canada": "ca",
    "Switzerland": "ch",
    "Cameroon": "cm",
    "Brazil": "br",
    "Serbia": "rs",
    "Uruguay": "uy",
    "South Korea": "kr",
    "Portugal": "pt",
    "Ghana": "gh",
}

WC2022_FIXTURES = [
    # Group A
    ("Group A","Qatar","Ecuador"),
    ("Group A","Senegal","Netherlands"),
    ("Group A","Qatar","Senegal"),
    ("Group A","Netherlands","Ecuador"),
    ("Group A","Netherlands","Qatar"),
    ("Group A","Ecuador","Senegal"),
    # Group B
    ("Group B","England","Iran"),
    ("Group B","USA","Wales"),
    ("Group B","Wales","Iran"),
    ("Group B","England","USA"),
    ("Group B","Wales","England"),
    ("Group B","Iran","USA"),
    # Group C
    ("Group C","Argentina","Saudi Arabia"),
    ("Group C","Mexico","Poland"),
    ("Group C","Poland","Saudi Arabia"),
    ("Group C","Argentina","Mexico"),
    ("Group C","Poland","Argentina"),
    ("Group C","Saudi Arabia","Mexico"),
    # Group D
    ("Group D","Denmark","Tunisia"),
    ("Group D","France","Australia"),
    ("Group D","Tunisia","Australia"),
    ("Group D","France","Denmark"),
    ("Group D","Australia","Denmark"),
    ("Group D","Tunisia","France"),
    # Group E
    ("Group E","Germany","Japan"),
    ("Group E","Spain","Costa Rica"),
    ("Group E","Japan","Costa Rica"),
    ("Group E","Spain","Germany"),
    ("Group E","Japan","Spain"),
    ("Group E","Costa Rica","Germany"),
    # Group F
    ("Group F","Morocco","Croatia"),
    ("Group F","Belgium","Canada"),
    ("Group F","Belgium","Morocco"),
    ("Group F","Croatia","Canada"),
    ("Group F","Croatia","Belgium"),
    ("Group F","Canada","Morocco"),
    # Group G
    ("Group G","Switzerland","Cameroon"),
    ("Group G","Brazil","Serbia"),
    ("Group G","Cameroon","Serbia"),
    ("Group G","Brazil","Switzerland"),
    ("Group G","Serbia","Switzerland"),
    ("Group G","Cameroon","Brazil"),
    # Group H
    ("Group H","Uruguay","South Korea"),
    ("Group H","Portugal","Ghana"),
    ("Group H","South Korea","Ghana"),
    ("Group H","Portugal","Uruguay"),
    ("Group H","South Korea","Portugal"),
    ("Group H","Ghana","Uruguay")
]

DB_PATH = "bolao_2026_dev.db"

def flag_url(team: str) -> str:
    code = TEAM_TO_CODE.get(team)
    return f"https://flagcdn.com/h20/{code}.png"

def _day_suffix(d):
    return "th" if 11 <= d % 100 <= 13 else {1:"st",2:"nd",3:"rd"}.get(d % 10, "th")

def fmt_kickoff(iso_utc: str, tz: str = LOCAL_TZ) -> str:
    """
    Format an ISO UTC timestamp (e.g., '2024-10-26T19:00:00Z') into Brazilian style:
    'dd/mm/YYYY HH:MM' in the given local timezone.
    """
    if not iso_utc:
        return ""
    try:
        dt_utc = datetime.fromisoformat(iso_utc.replace("Z", "+00:00"))
    except Exception:
        return ""
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    dt_local = dt_utc.astimezone(ZoneInfo(tz))
    return dt_local.strftime("%d/%m/%Y %H:%M")

def check_password(pwd, real_password):
    if pwd == real_password:
        return True
    else:
        return False

def seed_wc2022(conn):
    cur = conn.execute("SELECT COUNT(*) AS c FROM match")
    if cur.fetchone()["c"] > 0:
        return 0
    conn.executemany("INSERT INTO match (phase,home,away) VALUES (?,?,?)", WC2022_FIXTURES)
    conn.commit()
    return len(WC2022_FIXTURES)

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def list_teams():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT team FROM (
              SELECT DISTINCT home AS team FROM match
              UNION
              SELECT DISTINCT away AS team FROM match
            )
            ORDER BY team
        """).fetchall()
    return [r["team"] for r in rows]
