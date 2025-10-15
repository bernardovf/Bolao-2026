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

DB_PATH  = os.getenv("DB_PATH", "bolao_2026_dev.db")

PHASE_LOCKS = {
    "Round of 16": True,   # True = locked (bets closed)
    "Quarterfinals": False,
    "Semifinals":   False,
    "Final":        True,
    "General":      True
}

unlocks = {
    "oitavas": True,
    "quartas": True,
    "semi": True,
    "final3": True,
}


def phase_locked(phase: str) -> bool:
    return bool(PHASE_LOCKS.get(phase, False))

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
