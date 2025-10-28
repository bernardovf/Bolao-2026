from flask import Flask, render_template_string, request, redirect, url_for, flash, session, abort
import sqlite3, os
from templates import BASE, HOME, LOGIN, MATCHES, PALPITES, FLAT_PHASE_PAGE, RANKING, MATCH_BREAKDOWN
from utils import flag_url, fmt_kickoff, check_password, get_conn, list_teams, _fetch_user_bets, _fetch_phase_rows, \
    _select_match_ids, require_login, _calc_points, _compute_group_table_from_bets, phase_locked, rank_best_thirds, \
    team_color, DRAW_COLOR, abbr3, fmt_kickoff_pt
from datetime import datetime
from collections import defaultdict
from constants import unlocks, PHASE_ROUTES, PHASE_PAGES


APP_SECRET = os.environ.get("SECRET_KEY", "dev-secret")

app = Flask(__name__)
app.config["SECRET_KEY"] = APP_SECRET
app.jinja_env.globals.update(flag=flag_url)
app.jinja_env.filters["fmtkick"] = fmt_kickoff
app.jinja_env.filters["abbr3"] = abbr3

@app.template_filter("fmt_kickoff_pt")
def _fmt_kickoff_pt_filter(iso_utc, tz="America/Sao_Paulo"):
    # accents=False to match "SABADO"; set to True if you want "SÁBADO"
    return fmt_kickoff_pt(iso_utc, tz=tz, accents=False)
app.jinja_env.filters["fmt_kickoff_pt"] = fmt_kickoff_pt


# ---------- Routes ----------
@app.route("/")
def index():
    return render_template_string(
        BASE,
        content=render_template_string(HOME, unlocks=unlocks),
    )

@app.route("/save_picks/<phase_slug>", methods=["POST"])
def save_picks(phase_slug):
    # login
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    info = PHASE_ROUTES.get(phase_slug)
    if not info:
        flash("Unknown phase.")
        return redirect(url_for("index"))
    phases, back_ep = info  # e.g. (["Group A",...,"Group H"], "fase_grupos") for "groups"

    # ---- lock policy
    if phase_slug == "groups":
        if phase_locked("Groups"):
            flash("Apostas encerradas para a Fase de Grupos.")
            return redirect(url_for("fase_page", phase_slug="groups"))
    else:
        if any(phase_locked(p) for p in phases):
            flash("Apostas encerradas para esta fase.")
            return redirect(url_for(back_ep))

    uid = session["id"]

    # ---- upsert all scores present in the POST
    with get_conn() as conn:
        mids = _select_match_ids(conn, phases)  # SELECT id FROM fixtures WHERE phase IN (...)
        saved = 0
        for mid in mids:
            h_raw = request.form.get(f"h_{mid}")
            a_raw = request.form.get(f"a_{mid}")

            # skip if either field wasn't posted or is blank
            if h_raw is None or a_raw is None:
                continue
            if h_raw.strip() == "" or a_raw.strip() == "":
                continue

            try:
                hg, ag = int(h_raw), int(a_raw)
                if hg < 0 or ag < 0:
                    continue
            except ValueError:
                continue

            conn.execute("""
                INSERT INTO bet (user_id, match_id, home_goals, away_goals)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, match_id) DO UPDATE SET
                  home_goals = excluded.home_goals,
                  away_goals = excluded.away_goals
            """, (uid, mid, hg, ag))
            saved += 1
        conn.commit()

    flash(f"Saved {saved} pick(s).")

    # ---- only now, redirect back; keep the same group if we were on groups
    if phase_slug == "groups":
        sel = request.form.get("group")  # hidden input from the form
        if sel:
            return redirect(url_for("fase_page", phase_slug="groups", group=sel))
        return redirect(url_for("fase_page", phase_slug="groups"))

    return redirect(url_for(back_ep))

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
        return redirect(url_for("index"))

    return render_template_string(BASE, content=render_template_string(LOGIN))

@app.route("/match/<int:match_id>")
def match_detail(match_id: int):
    # same auth guard pattern
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    with get_conn() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Fixture header
        cur.execute("""
            SELECT id, phase, home, away, kickoff_utc, final_home_goals, final_away_goals
            FROM fixtures
            WHERE id = ?
        """, (match_id,))
        fixture = cur.fetchone()
        if not fixture:
            abort(404)

        # Total bets
        cur.execute("SELECT COUNT(*) AS n FROM bet WHERE match_id = ?", (match_id,))
        total_bets = cur.fetchone()["n"]

        # Outcome breakdown (home/draw/away) with percentages
        cur.execute("""
            WITH x AS (
              SELECT
                CASE
                  WHEN home_goals > away_goals THEN 'home'
                  WHEN home_goals = away_goals THEN 'draw'
                  ELSE 'away'
                END AS outcome
              FROM bet
              WHERE match_id = ?
            ),
            c AS (
              SELECT outcome, COUNT(*) AS cnt FROM x GROUP BY outcome
            )
            SELECT outcome, cnt,
                   CASE WHEN (SELECT SUM(cnt) FROM c) = 0 THEN 0.0
                        ELSE ROUND(100.0 * cnt * 1.0 / (SELECT SUM(cnt) FROM c), 1)
                   END AS pct
            FROM c;
        """, (match_id,))
        raw_outcomes = cur.fetchall()

        label_map = {
            "home": f"Vitória {fixture['home']}",
            "draw": "Empate",
            "away": f"Vitória {fixture['away']}",
        }
        outcomes = [
            {"outcome": r["outcome"], "cnt": r["cnt"], "pct": r["pct"], "label": label_map.get(r["outcome"], r["outcome"])}
            for r in raw_outcomes
        ]
        # keep order home/draw/away
        outcomes.sort(key=lambda o: {"home": 1, "draw": 2, "away": 3}.get(o["outcome"], 99))

        # Top exact scores
        cur.execute("""
            SELECT home_goals, away_goals, COUNT(*) AS cnt
            FROM bet
            WHERE match_id = ?
            GROUP BY home_goals, away_goals
            ORDER BY cnt DESC, home_goals, away_goals
            LIMIT 10;
        """, (match_id,))
        top_scores = cur.fetchall()

        # List all picks with user names
        cur.execute("""
            SELECT u.user_name, b.home_goals, b.away_goals
            FROM bet b
            JOIN users u ON u.id = b.user_id
            WHERE b.match_id = ?
            ORDER BY u.user_name COLLATE NOCASE;
        """, (match_id,))
        picks = cur.fetchall()

        # --- build stacked bar values (safe for 0 total) ---
        tot = sum(r["cnt"] for r in raw_outcomes) or 1
        by = {r["outcome"]: r["cnt"] for r in raw_outcomes}
        home_cnt = by.get("home", 0)
        draw_cnt = by.get("draw", 0)
        away_cnt = by.get("away", 0)

        stack = {
            "home_pct": int(100 * home_cnt / tot),
            "draw_pct": int(100 * draw_cnt / tot),
            "away_pct": int(100 * away_cnt / tot),
            "home_cnt": home_cnt,
            "draw_cnt": draw_cnt,
            "away_cnt": away_cnt,
            "total": tot if tot != 1 or (home_cnt + draw_cnt + away_cnt) == 1 else 0,  # only for display
        }

    home_color = team_color(fixture["home"])
    away_color = team_color(fixture["away"])
    colors = {"home": home_color, "draw": DRAW_COLOR, "away": away_color}

    def rgba(hex_color: str, a: float) -> str:
        # hex like "#RRGGBB" -> "rgba(r,g,b,a)"
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r},{g},{b},{a})"

    # after you compute:
    # colors = {"home": team_color(...), "draw": DRAW_COLOR, "away": team_color(...)}

    bg = {
        "home": rgba(colors["home"], 0.5),  # soft tint
        "draw": rgba(colors["draw"], 0.2),
        "away": rgba(colors["away"], 0.5),
    }
    # a stronger color for the left border accent
    edge = {
        "home": colors["home"],
        "draw": colors["draw"],
        "away": colors["away"],
    }

    html = render_template_string(
        MATCH_BREAKDOWN,
        fixture=fixture,
        outcomes=outcomes,
        top_scores=top_scores,
        total_bets=total_bets,
        picks=picks,
        back_url=request.referrer or url_for("index"),
        stack=stack,
        colors=colors,  # <-- pass to template
        bg=bg,
        edge=edge,
    )
    return render_template_string(BASE, content=html)

@app.route("/fase/<phase_slug>")
def fase_page(phase_slug):
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    page = PHASE_PAGES.get(phase_slug)
    if not page:
        flash("Página de fase desconhecida.")
        return redirect(url_for("index"))

    with get_conn() as conn:
        conn.row_factory = sqlite3.Row
        rows = _fetch_phase_rows(conn, page["phases"])
        bets = _fetch_user_bets(conn, session["id"])

    # lock policy
    locked = phase_locked("Groups") if phase_slug == "groups" else any(
        phase_locked(p) for p in page["phases"]
    )

    if page["template"] == "groups":
        groups = defaultdict(list)
        for r in rows:
            groups[r["phase"]].append(dict(r))  # <-- IMPORTANT: dict()

        group_order = [f"Group {c}" for c in "ABCDEFGHIJKL"]
        selected_group = next((g for g in group_order if groups.get(g)), group_order[0])

        # honor ?group=...
        qs_group = request.args.get("group")
        if qs_group in group_order and groups.get(qs_group):
            selected_group = qs_group

        points = {}
        for g in groups.values():
            for m in g:
                b = bets.get(m["id"])
                pick_h = (b or {}).get("home_goals")
                pick_a = (b or {}).get("away_goals")
                points[m["id"]] = _calc_points(
                    pick_h, pick_a,
                    m.get("final_home_goals"), m.get("final_away_goals")
                )

        # Build standings for ALL groups first
        standings_by_group = {}
        for gname, grows in groups.items():
            standings_by_group[gname] = _compute_group_table_from_bets(grows, bets)

        # Determine the 8 best third-placed teams (by user bets)
        best3 = rank_best_thirds(standings_by_group)

        # The table to display is the selected group's table
        standings = standings_by_group.get(selected_group, [])

        html = render_template_string(
            MATCHES,
            groups=groups,
            group_order=group_order,
            bets=bets,
            selected_group=selected_group,
            locked=locked,
            points=points,
            standings=standings,  # current group's table
            best3=best3,  # <-- pass set of team names
        )
    else:
        matches = [dict(r) for r in rows]
        points = {}
        for m in matches:
            b = bets.get(m["id"])
            pick_h = (b or {}).get("home_goals")
            pick_a = (b or {}).get("away_goals")
            points[m["id"]] = _calc_points(
                pick_h, pick_a,
                m.get("final_home_goals"), m.get("final_away_goals")
            )

        html = render_template_string(
            FLAT_PHASE_PAGE,
            title=page["title"],
            phase_slug=phase_slug,
            button_label=page["button"],
            matches=matches,
            bets=bets,
            locked=locked,
            action_url=None,
            points=points,  # <-- pass it
        )

    return render_template_string(BASE, content=html)

@app.route("/ranking")
def ranking():
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    sql = """
    WITH scored AS (
      SELECT
        u.id        AS user_id,
        u.user_name AS user_name,
        f.phase,
        -- pontos por aposta
        CASE
          WHEN f.final_home_goals IS NULL OR f.final_away_goals IS NULL THEN NULL
          WHEN b.home_goals = f.final_home_goals AND b.away_goals = f.final_away_goals THEN 10
          WHEN ((b.home_goals > b.away_goals AND f.final_home_goals > f.final_away_goals) OR
                (b.home_goals < b.away_goals AND f.final_home_goals < f.final_away_goals) OR
                (b.home_goals = b.away_goals AND f.final_home_goals = f.final_away_goals)) THEN 5
          ELSE 0
        END AS points,
        CASE
          WHEN f.final_home_goals IS NULL OR f.final_away_goals IS NULL THEN NULL
          WHEN b.home_goals = f.final_home_goals AND b.away_goals = f.final_away_goals THEN 1
          WHEN ((b.home_goals > b.away_goals AND f.final_home_goals > f.final_away_goals) OR
                (b.home_goals < b.away_goals AND f.final_home_goals < f.final_away_goals) OR
                (b.home_goals = b.away_goals AND f.final_home_goals = f.final_away_goals)) THEN 0
          ELSE 0
        END AS number_exact_matches,
        CASE
          WHEN f.final_home_goals IS NULL OR f.final_away_goals IS NULL THEN NULL
          WHEN b.home_goals = f.final_home_goals AND b.away_goals = f.final_away_goals THEN 0
          WHEN ((b.home_goals > b.away_goals AND f.final_home_goals > f.final_away_goals) OR
                (b.home_goals < b.away_goals AND f.final_home_goals < f.final_away_goals) OR
                (b.home_goals = b.away_goals AND f.final_home_goals = f.final_away_goals)) THEN 1
          ELSE 0
        END AS number_result_matches
      FROM users u
      LEFT JOIN bet b      ON b.user_id = u.id
      LEFT JOIN fixtures f ON f.id      = b.match_id
      -- somente jogos com resultado oficial contam
      WHERE f.final_home_goals IS NOT NULL AND f.final_away_goals IS NOT NULL
    )
    SELECT
      user_id,
      user_name,
      COALESCE(SUM(points),0) AS total_points,
      COALESCE(SUM(number_exact_matches),0) AS number_exact_matches,
      COALESCE(SUM(number_result_matches),0) AS number_result_matches,

      -- breakdown por fase
      COALESCE(SUM(CASE WHEN phase LIKE 'Group %'    THEN points END),0) AS pts_grupos,
      COALESCE(SUM(CASE WHEN phase = 'Round of 32'   THEN points END),0) AS pts_r32,        -- opcional p/ 2026
      COALESCE(SUM(CASE WHEN phase = 'Round of 16'   THEN points END),0) AS pts_oitavas,
      COALESCE(SUM(CASE WHEN phase = 'Quarterfinals' THEN points END),0) AS pts_quartas,
      COALESCE(SUM(CASE WHEN phase = 'Semifinals'    THEN points END),0) AS pts_semi,
      COALESCE(SUM(CASE WHEN phase = 'Third Place'   THEN points END),0) AS pts_terceiro,
      COALESCE(SUM(CASE WHEN phase = 'Final'         THEN points END),0) AS pts_final

    FROM scored
    GROUP BY user_id, user_name
    ORDER BY total_points DESC, user_name ASC;
    """

    with get_conn() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql).fetchall()

    return render_template_string(
        BASE,
        content=render_template_string(RANKING, rows=rows, current_id=session["id"]),
    )

@app.route("/fase_grupos")
def fase_grupos():
    return redirect(url_for("fase_page", phase_slug="groups"))

@app.route("/decima_sexta")
def decima_sexta():
    return redirect(url_for("fase_page", phase_slug="decima_sexta"))

@app.route("/oitavas_final")
def oitavas_final():
    return redirect(url_for("fase_page", phase_slug="oitavas"))

@app.route("/quartas_final")
def quartas_final():
    return redirect(url_for("fase_page", phase_slug="quartas"))

@app.route("/semi_final")
def semi_final():
    return redirect(url_for("fase_page", phase_slug="semi"))

@app.route("/final_terceiro")
def final_terceiro():
    return redirect(url_for("fase_page", phase_slug="final"))

@app.route("/palpites", methods=["GET", "POST"])
def palpites():
    # login gate
    if not session.get("id"):
        flash("Please log in.")
        return redirect(url_for("login"))

    uid = session["id"]

    if request.method == "POST":
        # hard block when locked
        if phase_locked("General"):
            flash("Palpites gerais estão encerrados.")
            return redirect(url_for("palpites"))

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
    return render_template_string(
        BASE,
        content=render_template_string(
            PALPITES,
            row=row,
            teams=teams,
            locked=phase_locked("General"),   # <-- pass to template
        ),
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
