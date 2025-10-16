from datetime import datetime
import sqlite3
from constants import TEAM_TO_CODE, DB_PATH, PHASE_LOCKS

def _calc_points(pick_h, pick_a, real_h, real_a):
    """10 exact, 5 correct outcome, else 0. None if result/pick missing."""
    if pick_h is None or pick_a is None:
        return None
    if real_h is None or real_a is None:
        return None
    if pick_h == real_h and pick_a == real_a:
        return 10
    def outcome(h, a):  # 1 home win, -1 away win, 0 draw
        return (h > a) - (h < a)
    return 5 if outcome(pick_h, pick_a) == outcome(real_h, real_a) else 0

def require_login():
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))
    return None

def _fetch_user_bets(conn, uid):
    rows = conn.execute("""
        SELECT match_id, home_goals, away_goals
        FROM bet WHERE user_id = ?
    """, (uid,)).fetchall()
    return {r["match_id"]: dict(r) for r in rows}

def _fetch_phase_rows(conn, phases):
    placeholders = ",".join("?" * len(phases))
    return conn.execute(f"""
        SELECT id, phase, home, away, kickoff_utc,
               final_home_goals, final_away_goals
        FROM fixtures
        WHERE phase IN ({placeholders})
        ORDER BY datetime(kickoff_utc), id
    """, phases).fetchall()

def _select_match_ids(conn, phases):
    placeholders = ",".join("?" * len(phases))
    rows = conn.execute(
        f"SELECT id FROM fixtures WHERE phase IN ({placeholders}) ORDER BY id",
        phases
    ).fetchall()
    return [r[0] for r in rows]

def phase_locked(phase: str) -> bool:
    return bool(PHASE_LOCKS.get(phase, False))

def flag_url(team: str) -> str:
    code = TEAM_TO_CODE.get(team)
    return f"https://flagcdn.com/h20/{code}.png"

def _day_suffix(d):
    return "th" if 11 <= d % 100 <= 13 else {1:"st",2:"nd",3:"rd"}.get(d % 10, "th")

def fmt_kickoff(value):
    """
    Render ISO datetime (e.g., '2022-11-20T12:00:00Z' or '+00:00') as 'dd/mm HH:MM'.
    Keeps it in UTC (as your field name suggests). Adjust here if you want a TZ.
    """
    if not value:
        return ""
    s = str(value)
    # Accept 'Z' suffix or '+00:00'
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        # fallback: strip subseconds if present
        if "." in s:
            base, rest = s.split(".", 1)
            s = base + s[-6:]  # keep timezone part
            dt = datetime.fromisoformat(s)
        else:
            return str(value)
    return dt.strftime("%d/%m %H:%M")

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
