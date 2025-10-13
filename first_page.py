from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
import sqlite3, os
from datetime import datetime, timezone
from collections import defaultdict

APP_SECRET = os.environ.get("SECRET_KEY", "dev-secret")
DB_PATH = "users.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = APP_SECRET

# ---------- DB helpers ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

SCHEMA_USER = """
CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_name   TEXT NOT NULL,
  user_email  TEXT NOT NULL UNIQUE,
  password_hash    TEXT NOT NULL,       -- stores a HASH (not plaintext)
  created_at  TEXT NOT NULL
);
"""

SCHEMA_MATCH = """
CREATE TABLE IF NOT EXISTS match (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  phase TEXT NOT NULL,
  home  TEXT NOT NULL,
  away  TEXT NOT NULL
);
"""

SCHEMA_BET = """
CREATE TABLE IF NOT EXISTS bet (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id  INTEGER NOT NULL,
  match_id INTEGER NOT NULL,
  home_goals INTEGER NOT NULL,
  away_goals INTEGER NOT NULL,
  UNIQUE(user_id, match_id),
  FOREIGN KEY(user_id) REFERENCES user(id),
  FOREIGN KEY(match_id) REFERENCES match(id)
);
"""

def ensure_schema():
    with get_conn() as conn:
        conn.execute(SCHEMA_USER)
        conn.execute(SCHEMA_MATCH)
        conn.execute(SCHEMA_BET)
        conn.commit()

ensure_schema()

# ---------- Fixtures: FIFA World Cup 2022 (all 64) ----------
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

def seed_wc2022():
    with get_conn() as conn:
        cur = conn.execute("SELECT COUNT(*) AS c FROM match")
        if cur.fetchone()["c"] > 0:
            return 0
        conn.executemany("INSERT INTO match (phase,home,away) VALUES (?,?,?)", WC2022_FIXTURES)
        conn.commit()
        return len(WC2022_FIXTURES)

# ---------- Templates ----------
BASE = """<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/mvp.css">
<style>
  .fixtures { max-width: 920px; }
  .fixtures table { width: 100%; }
  .index-col { width: 48px; text-align: center; }
  .fixture-cell { padding: .45rem .6rem; }

  /* one-line layout */
  .fixture-row {
    display: grid;
    grid-template-columns: 1fr 36px 16px 36px 1fr; /* ↓ narrower inputs */
    align-items: center;
    column-gap: 10px;
  }
  .team { font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .team.left  { text-align: right; }
  .team.right { text-align: left;  }
  .sep { text-align: center; }

  /* smaller score boxes */
  .score {
    display: inline-block !important;
    width: 36px !important;     /* was 70px */
    max-width: 36px !important;
    text-align: center;
    font-size: 0.9rem;          /* slight text shrink */
    padding: 4px 6px;           /* tighter padding */
    margin: 0;
  }

  /* optional: even smaller on phones */
  @media (max-width: 640px) {
    .fixture-row { grid-template-columns: 1fr 36px 14px 36px 1fr; }
    .score { width: 40px !important; max-width: 40px !important; font-size: 0.85rem; }
  }

  /* optional: hide number spinners for cleaner look */
  input[type=number].score::-webkit-outer-spin-button,
  input[type=number].score::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
  input[type=number].score { -moz-appearance: textfield; }
</style>
<main>
<header>
  <h1>Pick'Em</h1>
  {% if session.get('uid') %}
    <small>Logged in as {{ session.get('email') }}</small> · <a href="{{ url_for('logout') }}">Logout</a>
  {% endif %}
  {% for m in get_flashed_messages() %}<p>{{ m }}</p>{% endfor %}
</header>
{{ content|safe }}
</main>
"""

HOME = """
<h2>Welcome!</h2>
<p>
  {% if not session.get('uid') %}
    <a class="button" href="{{ url_for('login') }}">Login</a>
  {% else %}
    <a class="button" href="{{ url_for('matches') }}">Go to Matches</a>
  {% endif %}
</p>
<p><a href="{{ url_for('seed_wc2022_route') }}">[Seed World Cup 2022 fixtures]</a> (dev only)</p>
"""

LOGIN = """
<h2>Login</h2>
<form method="post" action="{{ url_for('login') }}">
  <label>Email <input type="email" name="email" required autocomplete="email"></label>
  <label>Password <input type="password" name="password" required autocomplete="current-password"></label>
  <button>Login</button>
</form>
"""

MATCHES = """
<h2>World Cup 2022 — Enter your predictions</h2>
<p><a class="button" href="{{ url_for('index') }}">Home</a></p>

<div class="fixtures">
{% for group_name in group_order %}
  {% if groups.get(group_name) %}
  <h3>{{ group_name }}</h3>

  <form method="post" action="{{ url_for('save_group', group=group_name) }}">
    <table>
      <thead>
        <tr>
          <th class="index-col">#</th>
          <th>Fixture</th>
        </tr>
      </thead>
      <tbody>
      {% for m in groups[group_name] %}
        {% set b = bets.get(m['id']) %}
        <tr>
          <td class="index-col">{{ loop.index }}</td>
            <td class="fixture-cell">
              <div class="fixture-row">
                <div class="team left">{{ m['home'] }}</div>
                <input class="score" type="number" min="0" name="h_{{ m['id'] }}" value="{{ b['home_goals'] if b else '' }}">
                <div class="sep">x</div>
                <input class="score" type="number" min="0" name="a_{{ m['id'] }}" value="{{ b['away_goals'] if b else '' }}">
                <div class="team right">{{ m['away'] }}</div>
              </div>
            </td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
    <div class="save-row">
      <button>Save {{ group_name }}</button>
    </div>
  </form>
  {% endif %}
{% endfor %}

{% if knockouts %}
  <h3>Knockout Stage</h3>
  <table>
    <thead><tr><th class="index-col">#</th><th>Phase</th><th>Fixture</th><th>Action</th></tr></thead>
    <tbody>
    {% for m in knockouts %}
      {% set b = bets.get(m['id']) %}
      <tr>
        <td class="index-col">{{ loop.index }}</td>
        <td>{{ m['phase'] }}</td>
        <td class="fixture-cell">
          <div class="fixture-grid">
            <div class="team-left">{{ m['home'] }}</div>
            <form method="post" action="{{ url_for('place_bet', match_id=m['id']) }}" style="display:contents;">
              <input class="score" type="number" min="0" name="home_goals" value="{{ b['home_goals'] if b else '' }}">
              <div class="sep">x</div>
              <input class="score" type="number" min="0" name="away_goals" value="{{ b['away_goals'] if b else '' }}">
              <div class="team-right">{{ m['away'] }}</div>
          </div>
        </td>
        <td>
              <button>Save</button>
            </form>
        </td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
{% endif %}
</div>
"""

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template_string(BASE, content=render_template_string(HOME))

@app.route("/seed_wc2022")
def seed_wc2022_route():
    n = seed_wc2022()
    flash("Seeded fixtures." if n else "Fixtures already present.")
    return redirect(url_for("index"))

@app.route("/save_group/<group>", methods=["POST"])
def save_group(group):
    # require login
    if not session.get("uid"):
        flash("Please log in.")
        return redirect(url_for("login"))

    # get all match IDs for this group
    with get_conn() as conn:
        mids = [r["id"] for r in conn.execute(
            "SELECT id FROM match WHERE phase=? ORDER BY id", (group,)
        ).fetchall()]

        saved = 0
        for mid in mids:
            h_key, a_key = f"h_{mid}", f"a_{mid}"
            h_raw, a_raw = request.form.get(h_key), request.form.get(a_key)
            if h_raw is None and a_raw is None:
                continue
            # allow empty fields to mean "skip"
            if (h_raw or "").strip() == "" or (a_raw or "").strip() == "":
                continue
            try:
                hg, ag = int(h_raw), int(a_raw)
                if hg < 0 or ag < 0:
                    raise ValueError
            except ValueError:
                continue  # silently skip invalid rows; or flash per-row if you prefer

            # upsert
            cur = conn.execute(
                "UPDATE bet SET home_goals=?, away_goals=? WHERE user_id=? AND match_id=?",
                (hg, ag, session["uid"], mid)
            )
            if cur.rowcount == 0:
                conn.execute(
                    "INSERT INTO bet (user_id, match_id, home_goals, away_goals) VALUES (?,?,?,?)",
                    (session["uid"], mid, hg, ag)
                )
            saved += 1
        conn.commit()

    flash(f"Saved {saved} pick(s) for {group}.")
    return redirect(url_for("matches"))


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        pwd   = request.form.get("password") or ""
        if not email or not pwd:
            flash("Email and password are required.")
            return redirect(url_for("login"))

        with get_conn() as conn:
            row = conn.execute(
                "SELECT id, user_name, user_email, password_hash FROM user WHERE user_email=?",
                (email,)
            ).fetchone()

        if not row or not check_password_hash(row["password_hash"], pwd):
            flash("Invalid email or password.")
            return redirect(url_for("login"))

        session["uid"] = row["id"]
        session["email"] = row["user_email"]
        session["name"] = row["user_name"]
        flash("Logged in.")
        return redirect(url_for("matches"))

    return render_template_string(BASE, content=render_template_string(LOGIN))

def require_login():
    if not session.get("uid"):
        flash("Please log in.")
        return redirect(url_for("login"))
    return None

@app.route("/matches")
@app.route("/matches")
def matches():
    # login gate
    if not session.get("uid"):
        flash("Please log in.")
        return redirect(url_for("login"))

    with get_conn() as conn:
        all_matches = conn.execute("SELECT id, phase, home, away FROM match ORDER BY id").fetchall()
        my_bets = conn.execute(
            "SELECT match_id, home_goals, away_goals FROM bet WHERE user_id=?",
            (session["uid"],)
        ).fetchall()

    bets = {b["match_id"]: dict(b) for b in my_bets}

    # Split into group tables and knockouts
    groups = defaultdict(list)
    knockouts = []
    for m in all_matches:
        ph = m["phase"]
        if ph.startswith("Group "):   # e.g., "Group A"
            groups[ph].append(m)
        else:
            knockouts.append(m)

    # desired order of groups
    group_order = [f"Group {c}" for c in list("ABCDEFGH")]

    return render_template_string(
        BASE,
        content=render_template_string(
            MATCHES,
            groups=groups,
            group_order=group_order,
            knockouts=knockouts,
            bets=bets
        )
    )

@app.route("/bet/<int:match_id>", methods=["POST"])
def place_bet(match_id):
    # gate
    maybe_redirect = require_login()
    if maybe_redirect: return maybe_redirect

    try:
        hg = int(request.form.get("home_goals", ""))
        ag = int(request.form.get("away_goals", ""))
        if hg < 0 or ag < 0: raise ValueError
    except Exception:
        flash("Enter non-negative integers.")
        return redirect(url_for("matches"))

    with get_conn() as conn:
        # upsert: try update first; if no row, insert
        cur = conn.execute(
            "UPDATE bet SET home_goals=?, away_goals=? WHERE user_id=? AND match_id=?",
            (hg, ag, session["uid"], match_id)
        )
        if cur.rowcount == 0:
            conn.execute(
                "INSERT INTO bet (user_id, match_id, home_goals, away_goals) VALUES (?,?,?,?)",
                (session["uid"], match_id, hg, ag)
            )
        conn.commit()
    flash("Saved.")
    return redirect(url_for("matches"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
