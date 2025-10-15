from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import sqlite3, os
from templates import BASE, HOME, LOGIN, MATCHES, PALPITES, OITAVAS_PAGE, QUARTAS_PAGE, SEMI_PAGE, FINAL_PAGE
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
    unlocks = {
        "oitavas": True,
        "quartas": False,
        "semi":   False,
        "final3": False,
    }
    return render_template_string(
        BASE,
        content=render_template_string(HOME, unlocks=unlocks),
    )

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
    return redirect(url_for("fase_grupos"))

@app.route("/salvar_oitavas", methods=["POST"])
def salvar_oitavas():
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    with get_conn() as conn:
        # make rows dict-like
        conn.row_factory = sqlite3.Row

        # ✅ use the real table name that has rows
        mids = [r["id"] for r in conn.execute(
            "SELECT id FROM fixtures WHERE phase = ? ORDER BY id",
            ("Round of 16",)
        ).fetchall()]

        saved = 0
        for mid in mids:
            h_key, a_key = f"h_{mid}", f"a_{mid}"
            h_raw, a_raw = request.form.get(h_key), request.form.get(a_key)

            # both must be present & non-empty
            if not h_raw or not a_raw:
                continue
            try:
                hg, ag = int(h_raw), int(a_raw)
                if hg < 0 or ag < 0:
                    continue
            except ValueError:
                continue

            # ✅ single-statement UPSERT
            conn.execute("""
                INSERT INTO bet (user_id, match_id, home_goals, away_goals)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, match_id) DO UPDATE SET
                  home_goals = excluded.home_goals,
                  away_goals = excluded.away_goals
            """, (session["id"], mid, hg, ag))
            saved += 1

        conn.commit()

    flash(f"Saved {saved} pick(s).")
    return redirect(url_for("oitavas_final"))  # make sure this endpoint exists

@app.route("/salvar_quartas", methods=["POST"])
def salvar_quartas():
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    with get_conn() as conn:
        # make rows dict-like
        conn.row_factory = sqlite3.Row

        # ✅ use the real table name that has rows
        mids = [r["id"] for r in conn.execute(
            "SELECT id FROM fixtures WHERE phase = ? ORDER BY id",
            ("Quarterfinals",)
        ).fetchall()]

        saved = 0
        for mid in mids:
            h_key, a_key = f"h_{mid}", f"a_{mid}"
            h_raw, a_raw = request.form.get(h_key), request.form.get(a_key)

            # both must be present & non-empty
            if not h_raw or not a_raw:
                continue
            try:
                hg, ag = int(h_raw), int(a_raw)
                if hg < 0 or ag < 0:
                    continue
            except ValueError:
                continue

            # ✅ single-statement UPSERT
            conn.execute("""
                INSERT INTO bet (user_id, match_id, home_goals, away_goals)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, match_id) DO UPDATE SET
                  home_goals = excluded.home_goals,
                  away_goals = excluded.away_goals
            """, (session["id"], mid, hg, ag))
            saved += 1

        conn.commit()

    flash(f"Saved {saved} pick(s).")
    return redirect(url_for("quartas_final"))  # make sure this endpoint exists

@app.route("/salvar_semi", methods=["POST"])
def salvar_semi():
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    with get_conn() as conn:
        # make rows dict-like
        conn.row_factory = sqlite3.Row

        # ✅ use the real table name that has rows
        mids = [r["id"] for r in conn.execute(
            "SELECT id FROM fixtures WHERE phase = ? ORDER BY id",
            ("Semifinals",)
        ).fetchall()]

        saved = 0
        for mid in mids:
            h_key, a_key = f"h_{mid}", f"a_{mid}"
            h_raw, a_raw = request.form.get(h_key), request.form.get(a_key)

            # both must be present & non-empty
            if not h_raw or not a_raw:
                continue
            try:
                hg, ag = int(h_raw), int(a_raw)
                if hg < 0 or ag < 0:
                    continue
            except ValueError:
                continue

            # ✅ single-statement UPSERT
            conn.execute("""
                INSERT INTO bet (user_id, match_id, home_goals, away_goals)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, match_id) DO UPDATE SET
                  home_goals = excluded.home_goals,
                  away_goals = excluded.away_goals
            """, (session["id"], mid, hg, ag))
            saved += 1

        conn.commit()

    flash(f"Saved {saved} pick(s).")
    return redirect(url_for("semi_final"))  # make sure this endpoint exists

@app.route("/salvar_final", methods=["POST"])
def salvar_final():
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    with get_conn() as conn:
        # make rows dict-like
        conn.row_factory = sqlite3.Row

        # ✅ use the real table name that has rows
        phases = ("Third Place", "Final")
        placeholders = ",".join("?" * len(phases))
        mids = [r["id"] for r in conn.execute(
            f"SELECT id FROM fixtures WHERE phase IN ({placeholders}) ORDER BY id",
            phases
        ).fetchall()]

        saved = 0
        for mid in mids:
            h_key, a_key = f"h_{mid}", f"a_{mid}"
            h_raw, a_raw = request.form.get(h_key), request.form.get(a_key)

            # both must be present & non-empty
            if not h_raw or not a_raw:
                continue
            try:
                hg, ag = int(h_raw), int(a_raw)
                if hg < 0 or ag < 0:
                    continue
            except ValueError:
                continue

            # ✅ single-statement UPSERT
            conn.execute("""
                INSERT INTO bet (user_id, match_id, home_goals, away_goals)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, match_id) DO UPDATE SET
                  home_goals = excluded.home_goals,
                  away_goals = excluded.away_goals
            """, (session["id"], mid, hg, ag))
            saved += 1

        conn.commit()

    flash(f"Saved {saved} pick(s).")
    return redirect(url_for("final_terceiro"))  # make sure this endpoint exists

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
        return redirect(url_for("fase_grupos"))

    return render_template_string(BASE, content=render_template_string(LOGIN))

def require_login():
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))
    return None

@app.route("/fase_grupos")
def fase_grupos():
    # login gate
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    selected_group = request.args.get("group")

    with get_conn() as conn:
        # ⬇︎ include kickoff_utc here
        all_matches = conn.execute(
            "SELECT id, phase, home, away, kickoff_utc FROM match where phase like '%Group%' ORDER BY id "
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

@app.route("/oitavas_final")
def oitavas_final():
    # login gate
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    with get_conn() as conn:
        # make rows dict-like (or convert to dicts below)
        conn.row_factory = sqlite3.Row

        # ⚠️ Use the correct table name. If you inserted into "fixtures",
        # query fixtures; if your table is actually called "match", keep it.
        rows = conn.execute("""
            SELECT id, home, away, kickoff_utc
            FROM fixtures
            WHERE phase = ?
            ORDER BY datetime(kickoff_utc), id
        """, ("Round of 16",)).fetchall()

        my_bets = conn.execute("""
            SELECT match_id, home_goals, away_goals
            FROM bet
            WHERE user_id = ?
        """, (session["id"],)).fetchall()

    # map bets by match id
    bets = {b["match_id"]: dict(b) for b in my_bets}

    # either pass rows directly (Row supports dict-like access) or convert:
    matches = [dict(r) for r in rows]

    return render_template_string(
        BASE,
        content=render_template_string(
            OITAVAS_PAGE,
            matches=matches,   # ← was missing
            bets=bets
        ),
    )

@app.route("/quartas_final")
def quartas_final():
    # login gate
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    with get_conn() as conn:
        # make rows dict-like (or convert to dicts below)
        conn.row_factory = sqlite3.Row

        # ⚠️ Use the correct table name. If you inserted into "fixtures",
        # query fixtures; if your table is actually called "match", keep it.
        rows = conn.execute("""
            SELECT id, home, away, kickoff_utc
            FROM fixtures
            WHERE phase = ?
            ORDER BY datetime(kickoff_utc), id
        """, ("Quarterfinals",)).fetchall()

        my_bets = conn.execute("""
            SELECT match_id, home_goals, away_goals
            FROM bet
            WHERE user_id = ?
        """, (session["id"],)).fetchall()

    # map bets by match id
    bets = {b["match_id"]: dict(b) for b in my_bets}

    # either pass rows directly (Row supports dict-like access) or convert:
    matches = [dict(r) for r in rows]

    return render_template_string(
        BASE,
        content=render_template_string(
            QUARTAS_PAGE,
            matches=matches,   # ← was missing
            bets=bets
        ),
    )

@app.route("/semi_final")
def semi_final():
    # login gate
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    with get_conn() as conn:
        # make rows dict-like (or convert to dicts below)
        conn.row_factory = sqlite3.Row

        # ⚠️ Use the correct table name. If you inserted into "fixtures",
        # query fixtures; if your table is actually called "match", keep it.
        rows = conn.execute("""
            SELECT id, home, away, kickoff_utc
            FROM fixtures
            WHERE phase = ?
            ORDER BY datetime(kickoff_utc), id
        """, ("Semifinals",)).fetchall()

        my_bets = conn.execute("""
            SELECT match_id, home_goals, away_goals
            FROM bet
            WHERE user_id = ?
        """, (session["id"],)).fetchall()

    # map bets by match id
    bets = {b["match_id"]: dict(b) for b in my_bets}

    # either pass rows directly (Row supports dict-like access) or convert:
    matches = [dict(r) for r in rows]

    return render_template_string(
        BASE,
        content=render_template_string(
            SEMI_PAGE,
            matches=matches,   # ← was missing
            bets=bets
        ),
    )

@app.route("/final_terceiro")
def final_terceiro():
    # login gate
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    with get_conn() as conn:
        # make rows dict-like (or convert to dicts below)
        conn.row_factory = sqlite3.Row

        # ⚠️ Use the correct table name. If you inserted into "fixtures",
        # query fixtures; if your table is actually called "match", keep it.
        phases = ("Third Place", "Final")
        rows = conn.execute(f"""
            SELECT id, home, away, kickoff_utc
            FROM fixtures
            WHERE phase IN ({",".join("?" * len(phases))})
            ORDER BY CASE phase
                       WHEN 'Third Place' THEN 1
                       WHEN 'Final' THEN 2
                     END,
                     datetime(kickoff_utc), id
        """, phases).fetchall()

        my_bets = conn.execute("""
            SELECT match_id, home_goals, away_goals
            FROM bet
            WHERE user_id = ?
        """, (session["id"],)).fetchall()

    # map bets by match id
    bets = {b["match_id"]: dict(b) for b in my_bets}

    # either pass rows directly (Row supports dict-like access) or convert:
    matches = [dict(r) for r in rows]

    return render_template_string(
        BASE,
        content=render_template_string(
            FINAL_PAGE,
            matches=matches,   # ← was missing
            bets=bets
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
        return redirect(url_for("fase_grupos"))

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
    return redirect(url_for("fase_grupos"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("index"))

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
