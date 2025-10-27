from datetime import datetime
import sqlite3
from constants import TEAM_TO_CODE, DB_PATH, PHASE_LOCKS, TEAM_COLOR_FALLBACKS
from collections import defaultdict
from zoneinfo import ZoneInfo

# Uppercase, without accents (matches your example "SABADO")
WEEKDAY_PT_NOACC = ["SEGUNDA", "TERÇA", "QUARTA", "QUINTA", "SEXTA", "SÁBADO", "DOMINGO"]
# If you prefer accents, swap to this:
WEEKDAY_PT_ACC = ["SEGUNDA", "TERÇA", "QUARTA", "QUINTA", "SEXTA", "SÁBADO", "DOMINGO"]

ABBR_MAP = {
    "Brazil": "BRA", "Argentina": "ARG", "France": "FRA", "Germany": "GER",
    "England": "ENG", "Spain": "ESP", "Portugal": "POR", "Italy": "ITA",
    # …add the rest here (FIFA codes). Fallback will handle unknowns.
}

def abbr3(name: str) -> str:
    if not name:
        return ""
    return ABBR_MAP.get(name, name[:3]).upper()


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
    return f"https://flagcdn.com/h80/{code}.png"

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

def fmt_kickoff_pt(iso_utc: str, tz: str = "America/Sao_Paulo", accents: bool = False) -> str:
    # Accept "...Z" or "+00:00"
    dt_utc = datetime.fromisoformat(iso_utc.replace("Z", "+00:00"))
    local = dt_utc.astimezone(ZoneInfo(tz))
    names = WEEKDAY_PT_ACC if accents else WEEKDAY_PT_NOACC
    wd = names[local.weekday()]  # 0=Mon ... 6=Sun
    return f"{wd} {local:%d/%m %H:%M}"

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

def _match_outcome(h, a):
    if h > a: return 1   # home win
    if h < a: return -1  # away win
    return 0             # draw

def _compute_group_table_from_bets(fixtures_rows, bets_by_mid):
    """
    fixtures_rows: iterable of dict/Row with keys: id, phase ('Group A'..), home, away
    bets_by_mid:  {match_id: {'home_goals': int, 'away_goals': int}}
    Returns: list[dict] standings sorted with FIFA tiebreakers including head-to-head.
    """
    # base stats
    stats = {
        # team -> aggregate
        # we’ll also keep a per-opponent ledger for head-to-head recomputation
    }
    agg = defaultdict(lambda: {
        "team": "",
        "played": 0, "won": 0, "draw": 0, "lost": 0,
        "gf": 0, "ga": 0, "gd": 0, "pts": 0,
        "h2h": defaultdict(lambda: {"gf": 0, "ga": 0, "pts": 0})  # vs opponent
    })

    for m in fixtures_rows:
        mid = m["id"]
        bet = bets_by_mid.get(mid)
        if not bet:  # no bet -> ignore for table (tournament hasn’t “happened” in user’s prediction)
            continue
        if bet.get("home_goals") is None or bet.get("away_goals") is None:
            continue

        home, away = m["home"], m["away"]
        h, a = int(bet["home_goals"]), int(bet["away_goals"])
        res = _match_outcome(h, a)

        # init names
        agg[home]["team"] = home
        agg[away]["team"] = away

        # played
        agg[home]["played"] += 1
        agg[away]["played"] += 1

        # gf/ga
        agg[home]["gf"] += h; agg[home]["ga"] += a
        agg[away]["gf"] += a; agg[away]["ga"] += h

        # results & points
        if res == 1:
            agg[home]["won"]  += 1; agg[away]["lost"] += 1
            agg[home]["pts"]  += 3
            agg[home]["h2h"][away]["pts"] += 3
        elif res == -1:
            agg[away]["won"]  += 1; agg[home]["lost"] += 1
            agg[away]["pts"]  += 3
            agg[away]["h2h"][home]["pts"] += 3
        else:
            agg[home]["draw"] += 1; agg[away]["draw"] += 1
            agg[home]["pts"]  += 1; agg[away]["pts"]  += 1
            agg[home]["h2h"][away]["pts"] += 1
            agg[away]["h2h"][home]["pts"] += 1

        # head-to-head gf/ga
        agg[home]["h2h"][away]["gf"] += h; agg[home]["h2h"][away]["ga"] += a
        agg[away]["h2h"][home]["gf"] += a; agg[away]["h2h"][home]["ga"] += h

    # compute GD
    for t in agg.values():
        t["gd"] = t["gf"] - t["ga"]

    # base sort (points, gd, gf)
    table = list(agg.values())

    def _base_key(t):
        return (t["pts"], t["gd"], t["gf"])

    table.sort(key=_base_key, reverse=True)

    # head-to-head for tied clusters (2+ teams)
    i = 0
    while i < len(table):
        # find tie cluster with same base key
        j = i + 1
        while j < len(table) and _base_key(table[j]) == _base_key(table[i]):
            j += 1
        if j - i >= 2:
            # apply mini-league among tied teams
            tied = table[i:j]
            tied_names = {t["team"] for t in tied}

            def mini_row(team_name):
                pts = gd = gf = 0
                # recompute using only matches between tied teams via stored h2h ledger
                for opp in tied_names:
                    if opp == team_name: continue
                    r = agg[team_name]["h2h"][opp]
                    pts += r["pts"]
                    gf  += r["gf"]
                    gd  += (r["gf"] - r["ga"])
                return (pts, gd, gf)

            tied.sort(key=lambda t: (*mini_row(t["team"]),), reverse=True)

            # If still tied after h2h, keep current order or fallback to alphabetic:
            k = 0
            while k < len(tied):
                l = k + 1
                while l < len(tied) and mini_row(tied[l]["team"]) == mini_row(tied[k]["team"]):
                    l += 1
                if l - k >= 2:
                    # fallback: alphabetical to keep deterministic (instead of fair play / drawing lots)
                    tied[k:l] = sorted(tied[k:l], key=lambda t: t["team"])
                k = l

            # put back
            table[i:j] = tied
        i = j

    # add rank
    for pos, row in enumerate(table, start=1):
        row["rank"] = pos
    return table

def rank_best_thirds(standings_by_group):
    """
    standings_by_group: dict {"Group A": [rows...], "Group B": [rows...], ...}
    Each row has: team, pts, gd, gf, rank, etc (from _compute_group_table_from_bets).
    Returns a set of team names that are the 8 best third-placed sides
    using: points, goal difference, goals scored; fallback = alphabetical.
    """
    thirds = []
    for g, table in standings_by_group.items():
        # find the 3rd place row in this group's table
        for r in table:
            if r.get("rank") == 3:
                thirds.append({
                    "group": g,
                    "team": r["team"],
                    "pts": r["pts"],
                    "gd":  r["gd"],
                    "gf":  r["gf"],
                })
                break

    # sort by pts, gd, gf, then alphabetical to keep deterministic
    thirds.sort(key=lambda x: (x["pts"], x["gd"], x["gf"], x["team"]), reverse=True)

    # take top 8; return as a set of team names for quick membership checks
    best8 = {row["team"] for row in thirds[:8]}
    return best8


DRAW_COLOR = "#A3A3A3"

def team_color(name: str) -> str:
    # simple alias handling
    aliases = {
        "United States of America": "United States",
        "Korea, Republic of": "South Korea",
        "Cote d'Ivoire": "Ivory Coast",
    }
    key = aliases.get(name, name)
    return TEAM_COLOR_FALLBACKS.get(key, "#6366F1")  # default indigo
