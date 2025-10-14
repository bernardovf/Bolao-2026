from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import sqlite3, os
from templates import BASE, HOME, LOGIN, MATCHES, PALPITES
from utils import flag_url, fmt_kickoff, check_password, get_conn, list_teams
from datetime import datetime

APP_SECRET = os.environ.get("SECRET_KEY", "dev-secret")

app = Flask(__name__)
app.config["SECRET_KEY"] = APP_SECRET
app.jinja_env.globals.update(flag=flag_url)
app.jinja_env.filters["fmtkick"] = fmt_kickoff

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template_string(BASE, content=render_template_string(HOME))

@app.route("/save_group/<group>", methods=["POST"])
def save_group(group):
    # require login
    if not session.get("id"):
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
                (hg, ag, session["id"], mid)
            )
            if cur.rowcount == 0:
                conn.execute(
                    "INSERT INTO bet (user_id, match_id, home_goals, away_goals) VALUES (?,?,?,?)",
                    (session["id"], mid, hg, ag)
                )
            saved += 1
        conn.commit()

    flash(f"Saved {saved} pick(s) for {group}.")
    return redirect(url_for("matches"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user_name = (request.form.get("user_name") or "").strip().lower()
        pwd   = request.form.get("password") or ""
        if not user_name or not pwd:
            flash("Email and password are required.")
            return redirect(url_for("login"))

        with get_conn() as conn:
            row = conn.execute("SELECT id, user_name, password FROM users WHERE user_name=?", (user_name,)).fetchone()

        if not row or not check_password(pwd, row["password"]):
            flash("Invalid email or password.")
            return redirect(url_for("login"))

        session["user_name"] = row["user_name"]
        session["id"] = row["id"]
        flash("Logged in.")
        return redirect(url_for("matches"))

    return render_template_string(BASE, content=render_template_string(LOGIN))

def require_login():
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))
    return None

@app.route("/matches")
def matches():
    # login gate
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    selected_group = request.args.get("group")

    with get_conn() as conn:
        # ⬇︎ include kickoff_utc here
        all_matches = conn.execute(
            "SELECT id, phase, home, away, kickoff_utc FROM match ORDER BY id"
        ).fetchall()
        my_bets = conn.execute(
            "SELECT match_id, home_goals, away_goals FROM bet WHERE user_id=?",
            (session['id'],)
        ).fetchall()

    bets = {b["match_id"]: dict(b) for b in my_bets}

    # Split into groups
    from collections import defaultdict
    groups = defaultdict(list)
    for m in all_matches:
        ph = m["phase"]
        if ph.startswith("Group "):
            groups[ph].append(m)

    group_order = [f"Group {c}" for c in list("ABCDEFGH")]
    if selected_group not in group_order:
        selected_group = group_order[0]

    return render_template_string(
        BASE,
        content=render_template_string(
            MATCHES,
            groups=groups,
            group_order=group_order,
            bets=bets,
            selected_group=selected_group,
        ),
    )

@app.route("/palpites", methods=["GET", "POST"])
def palpites():
    # login gate
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    uid = session["id"]

    if request.method == "POST":
        data = {
            "artilheiro": (request.form.get("artilheiro") or "").strip(),
            "melhor_jogador": (request.form.get("melhor_jogador") or "").strip(),
            "melhor_jogador_jovem": (request.form.get("melhor_jogador_jovem") or "").strip(),
            "campeao": (request.form.get("campeao") or "").strip(),
            "vice_campeao": (request.form.get("vice_campeao") or "").strip(),
            "terceiro_colocado": (request.form.get("terceiro_colocado") or "").strip(),
        }

        with get_conn() as conn:
            cur = conn.execute(
                """UPDATE palpites_gerais
                   SET artilheiro=?, melhor_jogador=?, melhor_jogador_jovem=?,
                       campeao=?, vice_campeao=?, terceiro_colocado=?, updated_at=?
                   WHERE user_id=?""",
                (
                    data["artilheiro"], data["melhor_jogador"], data["melhor_jogador_jovem"],
                    data["campeao"], data["vice_campeao"], data["terceiro_colocado"],
                    datetime.utcnow().isoformat(timespec="seconds"), uid
                )
            )
            if cur.rowcount == 0:
                conn.execute(
                    """INSERT INTO palpites_gerais
                       (user_id, artilheiro, melhor_jogador, melhor_jogador_jovem,
                        campeao, vice_campeao, terceiro_colocado, updated_at)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        uid, data["artilheiro"], data["melhor_jogador"], data["melhor_jogador_jovem"],
                        data["campeao"], data["vice_campeao"], data["terceiro_colocado"],
                        datetime.utcnow().isoformat(timespec="seconds")
                    )
                )
            conn.commit()

        flash("Palpites salvos.")
        return redirect(url_for("palpites"))

    # GET → load current values
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM palpites_gerais WHERE user_id=?", (uid,)
        ).fetchone()

    teams = list_teams()
    return render_template_string(BASE, content=render_template_string(PALPITES, row=row, teams=teams))

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
            (hg, ag, session["id"], match_id)
        )
        if cur.rowcount == 0:
            conn.execute(
                "INSERT INTO bet (user_id, match_id, home_goals, away_goals) VALUES (?,?,?,?)",
                (session["id"], match_id, hg, ag)
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
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
