import pandas as pd
import math

TEAM_RATINGS = {
    "Mexico": (1800, 1.61, -1.84),
    "South Africa": (1526, 1.61, -1.74),
    "South Korea": (1754, 1.61, -1.79),
    "Czechia": (1691, 1.59, -1.70),
    "Canada": (1741, 1.55, -1.80),
    "Bosnia and Herzegovina": (1589, 1.50, -1.62),
    "Qatar": (1591, 1.36, -1.50),
    "Switzerland": (1781, 1.75, -1.88),
    "Brazil": (1885, 1.81, -1.95),
    "Morocco": (1736, 1.77, -2.01),
    "Haiti": (1583, 1.32, -1.48),
    "Scotland": (1684, 1.62, -1.74),
    "United States": (1765, 1.60, -1.68),
    "Paraguay": (1706, 1.64, -1.83),
    "Australia": (1747, 1.65, -1.82),
    "Turkey": (1771, 1.71, -1.83),
    "Germany": (1867, 1.82, -1.90),
    "Curaçao": (1520, 1.22, -1.37),
    "Ivory Coast": (1618, 1.76, -1.89),
    "Ecuador": (1793, 1.66, -1.96),
    "Netherlands": (1868, 1.82, -1.91),
    "Japan": (1833, 1.77, -1.96),
    "Sweden": (1701, 1.63, -1.69),
    "Tunisia": (1583, 1.64, -1.80),
    "Belgium": (1816, 1.74, -1.80),
    "Egypt": (1632, 1.68, -1.91),
    "Iran": (1757, 1.62, -1.79),
    "New Zealand": (1599, 1.60, -1.72),
    "Spain": (1979, 1.96, -2.04),
    "Cape Verde": (1489, 1.59, -1.75),
    "Saudi Arabia": (1616, 1.44, -1.64),
    "Uruguay": (1803, 1.62, -1.89),
    "France": (1939, 1.88, -1.95),
    "Senegal": (1727, 1.88, -2.06),
    "Iraq": (1653, 1.47, -1.66),
    "Norway": (1746, 1.81, -1.89),
    "Argentina": (1965, 1.86, -2.04),
    "Algeria": (1659, 1.75, -1.93),
    "Austria": (1749, 1.67, -1.81),
    "Jordan": (1628, 1.62, -1.73),
    "Portugal": (1874, 1.77, -1.87),
    "DR Congo": (1538, 1.66, -1.90),
    "Uzbekistan": (1711, 1.58, -1.80),
    "Colombia": (1855, 1.82, -1.92),
    "England": (1886, 1.81, -1.99),
    "Croatia": (1821, 1.72, -1.82),
    "Ghana": (1478, 1.59, -1.75),
    "Panama": (1699, 1.46, -1.61),
}

ALIASES = {
    "Korea Republic": "South Korea",
    "Czech Republic": "Czechia",
    "USA": "United States",
    "United States of America": "United States",
    "Türkiye": "Turkey",
    "Turkiye": "Turkey",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Democratic Republic of the Congo": "DR Congo",
    "Congo DR": "DR Congo",
    "Cabo Verde": "Cape Verde",
}

DRAW_THRESHOLD = 50

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def poisson(k, lam):
    return math.exp(-lam) * lam**k / math.factorial(k)

def calculate_lambdas(home_team, away_team):
    home = normalize_team(home_team)
    away = normalize_team(away_team)

    home_elo, home_att, home_def = TEAM_RATINGS[home]
    away_elo, away_att, away_def = TEAM_RATINGS[away]

    elo_diff = home_elo - away_elo

    # Total goals: stronger attacks increase it, stronger defenses reduce it
    total_goals = (
        2.55
        + 0.35 * ((home_att + away_att) - 3.30)
        - 0.25 * (((-home_def) + (-away_def)) - 3.70)
        + 0.15 * min(abs(elo_diff) / 300, 1)
    )

    total_goals = max(1.7, min(total_goals, 4.2))

    # Goal share: driven mostly by Elo, then attack/defense edge
    strength = (
        elo_diff / 220
        + 0.90 * (home_att - away_att)
        + 0.70 * ((-home_def) - (-away_def))
    )

    home_share = sigmoid(strength)

    lambda_home = total_goals * home_share
    lambda_away = total_goals * (1 - home_share)

    return lambda_home, lambda_away

def score_points(pred_home, pred_away, real_home, real_away):
    if pred_home == real_home and pred_away == real_away:
        return 10

    pred_diff = pred_home - pred_away
    real_diff = real_home - real_away

    pred_result = (pred_diff > 0) - (pred_diff < 0)
    real_result = (real_diff > 0) - (real_diff < 0)

    if pred_result == real_result:
        if pred_result == 0:
            return 5
        if pred_diff == real_diff:
            return 6.6
        return 3.3

    return 0

def normalize_team(team):
    team = str(team).strip()
    return ALIASES.get(team, team)

def get_phase_multiplier(phase):
    if not phase or (isinstance(phase, float) and math.isnan(phase)):
        return 1
    phase_lower = str(phase).lower()
    if 'grupo' in phase_lower:
        return 1
    elif '16 avos' in phase_lower or '16avos' in phase_lower:
        return 3
    elif 'oitava' in phase_lower:
        return 4
    elif 'quarta' in phase_lower:
        return 6
    elif 'semifinal' in phase_lower:
        return 8
    elif 'terceiro' in phase_lower or '3o' in phase_lower:
        return 8
    elif 'final' in phase_lower:
        return 12
    return 1

def get_result(home_goals, away_goals):
    if home_goals > away_goals:
        return "H"
    elif home_goals < away_goals:
        return "A"
    else:
        return "D"

def calculate_points(pred_home, pred_away, real_home, real_away, phase=None):
    multiplier = get_phase_multiplier(phase)
    pred_result = get_result(pred_home, pred_away)
    real_result = get_result(real_home, real_away)

    if pred_home == real_home and pred_away == real_away:
        return 6 * multiplier

    if pred_result == real_result:
        if pred_result == "D":
            return 3 * multiplier
        elif (pred_home - pred_away) == (real_home - real_away):
            return 4 * multiplier
        else:
            return 2 * multiplier

    return 0

def _pcts(ph, pa, match_bets):
    """Return (pct_score, pct_result) for a prediction vs the actual bet distribution.

    pct_score  = fraction of bets on the exact score (ph, pa).
    pct_result = fraction of bets with the same H/D/A direction.
    Both are floored at 1/n (as if one person bet it) to avoid division by zero.
    """
    n = len(match_bets)
    if n == 0:
        return 1.0, 1.0
    k_score  = match_bets.count((ph, pa))
    pct_score = k_score / n if k_score > 0 else 1 / n
    pred_dir = get_result(ph, pa)
    k_res    = sum(1 for (bh, ba) in match_bets if get_result(bh, ba) == pred_dir)
    pct_res  = k_res / n if k_res > 0 else 1 / n
    return pct_score, pct_res

def calculate_points_contrarian(ph, pa, rh, ra, phase=None, match_bets=None):
    """Base points × 1/√pct_score. Rewards rare exact-score picks."""
    base = calculate_points(ph, pa, rh, ra, phase)
    if base == 0 or not match_bets:
        return base
    pct_score, _ = _pcts(ph, pa, match_bets)
    return round(base / math.sqrt(pct_score), 2)

def calculate_points_contrarian_result(ph, pa, rh, ra, phase=None, match_bets=None):
    """Base points × 1/√pct_result. Rewards rare H/D/A direction picks."""
    base = calculate_points(ph, pa, rh, ra, phase)
    if base == 0 or not match_bets:
        return base
    _, pct_res = _pcts(ph, pa, match_bets)
    return round(base / math.sqrt(pct_res), 2)

def calculate_points_linear(ph, pa, rh, ra, phase=None, match_bets=None):
    """Base points × 1/pct_score (no sqrt). Stronger rarity reward than contrarian."""
    base = calculate_points(ph, pa, rh, ra, phase)
    if base == 0 or not match_bets:
        return base
    pct_score, _ = _pcts(ph, pa, match_bets)
    return round(base / pct_score, 2)

def calculate_points_linear_result(ph, pa, rh, ra, phase=None, match_bets=None):
    """Base points × 1/pct_result (no sqrt). Stronger rarity reward than contrarian."""
    base = calculate_points(ph, pa, rh, ra, phase)
    if base == 0 or not match_bets:
        return base
    _, pct_res = _pcts(ph, pa, match_bets)
    return round(base / pct_res, 2)

def score_prediction(ph, pa, rh, ra, phase, match_bets):
    """Compute all five scoring methods for one prediction. Returns a dict."""
    return {
        "pts":         calculate_points(ph, pa, rh, ra, phase),
        "pts_ctr":     calculate_points_contrarian(ph, pa, rh, ra, phase, match_bets),
        "pts_ctr_res": calculate_points_contrarian_result(ph, pa, rh, ra, phase, match_bets),
        "pts_lin":     calculate_points_linear(ph, pa, rh, ra, phase, match_bets),
        "pts_lin_res": calculate_points_linear_result(ph, pa, rh, ra, phase, match_bets),
    }

def elo_1x0_strategy(home_team, away_team, **_):
    home = normalize_team(home_team)
    away = normalize_team(away_team)

    home_elo = TEAM_RATINGS[home][0]
    away_elo = TEAM_RATINGS[away][0]

    if home_elo >= away_elo:
        return 1, 0
    else:
        return 0, 1

def elo_2x1_strategy(home_team, away_team, **_):
    home = normalize_team(home_team)
    away = normalize_team(away_team)

    home_elo = TEAM_RATINGS[home][0]
    away_elo = TEAM_RATINGS[away][0]

    if home_elo >= away_elo:
        return 2, 1
    else:
        return 1, 2

def elo_1x0_draw_strategy(home_team, away_team, **_):
    home = normalize_team(home_team)
    away = normalize_team(away_team)

    home_elo = TEAM_RATINGS[home][0]
    away_elo = TEAM_RATINGS[away][0]

    elo_diff = abs(home_elo - away_elo)

    if elo_diff <= DRAW_THRESHOLD:
        return 1, 1

    if home_elo > away_elo:
        return 1, 0
    else:
        return 0, 1

def elo_bolao_strategy(home_team, away_team, **_):
    home = normalize_team(home_team)
    away = normalize_team(away_team)

    home_elo = TEAM_RATINGS[home][0]
    away_elo = TEAM_RATINGS[away][0]

    elo_diff = home_elo - away_elo
    abs_diff = abs(elo_diff)

    if abs_diff <= DRAW_THRESHOLD:
        return 1, 1

    if abs_diff <= 180:
        return (1, 0) if elo_diff > 0 else (0, 1)

    if abs_diff <= 320:
        return (2, 1) if elo_diff > 0 else (1, 2)

    return (2, 0) if elo_diff > 0 else (0, 2)

def elo_tiered_strategy(home_team, away_team, **_):
    home = normalize_team(home_team)
    away = normalize_team(away_team)

    home_elo = TEAM_RATINGS[home][0]
    away_elo = TEAM_RATINGS[away][0]

    elo_diff = home_elo - away_elo
    abs_diff = abs(elo_diff)

    # Very balanced match -> draw
    if abs_diff <= DRAW_THRESHOLD:
        return 1, 1

    # Small favorite -> narrow win
    if abs_diff <= 150:
        if elo_diff > 0:
            return 1, 0
        else:
            return 0, 1

    # Clear favorite -> both teams may score
    if abs_diff <= 275:
        if elo_diff > 0:
            return 2, 1
        else:
            return 1, 2

    # Huge favorite -> clean win
    if abs_diff <= 425:
        if elo_diff > 0:
            return 2, 0
        else:
            return 0, 2

    # Massive mismatch
    if elo_diff > 0:
        return 3, 0
    else:
        return 0, 3

def best_expected_points_strategy(home_team, away_team, max_goals=6, **_):
    home = normalize_team(home_team)
    away = normalize_team(away_team)

    lambda_home, lambda_away = calculate_lambdas(home, away)

    possible_scores = []

    # Build probability distribution of actual scores
    actual_scores = []
    for hg in range(max_goals + 1):
        for ag in range(max_goals + 1):
            prob = poisson(hg, lambda_home) * poisson(ag, lambda_away)
            actual_scores.append((hg, ag, prob))

    # Evaluate each possible prediction by expected bolão points
    for pred_home in range(max_goals + 1):
        for pred_away in range(max_goals + 1):
            expected_points = 0

            for real_home, real_away, prob in actual_scores:
                expected_points += prob * score_points(
                    pred_home,
                    pred_away,
                    real_home,
                    real_away
                )

            possible_scores.append({
                "pred_home": pred_home,
                "pred_away": pred_away,
                "expected_points": expected_points
            })

    best = max(possible_scores, key=lambda x: x["expected_points"])

    return best["pred_home"], best["pred_away"]

def rating_strategy(home_team, away_team, **_):
    home = normalize_team(home_team)
    away = normalize_team(away_team)

    h_elo, h_att, h_def = TEAM_RATINGS[home]
    a_elo, a_att, a_def = TEAM_RATINGS[away]

    # Better defense is more negative, so use -def
    home_strength = (
        0.70 * (h_elo / 100)
        + 1.50 * h_att
        + 1.00 * (-h_def)
    )

    away_strength = (
        0.70 * (a_elo / 100)
        + 1.50 * a_att
        + 1.00 * (-a_def)
    )

    diff = home_strength - away_strength
    abs_diff = abs(diff)

    home_is_fav = diff > 0

    # Very balanced
    if abs_diff <= 0.35:
        return 1, 1

    # Small favorite
    if abs_diff <= 0.90:
        return (1, 0) if home_is_fav else (0, 1)

    # Clear favorite
    if abs_diff <= 1.60:
        return (2, 1) if home_is_fav else (1, 2)

    # Strong favorite
    if abs_diff <= 2.40:
        return (2, 0) if home_is_fav else (0, 2)

    # Very strong favorite
    return (3, 0) if home_is_fav else (0, 3)

def lean_low_strategy(home_team, away_team, **_):
    """Elo direction but always predict the minimum scoreline (1-0/0-1/1-1).
    Maximises exact-score hits at the cost of saldo coverage."""
    home = normalize_team(home_team)
    away = normalize_team(away_team)
    elo_diff = TEAM_RATINGS[home][0] - TEAM_RATINGS[away][0]
    if abs(elo_diff) <= DRAW_THRESHOLD:
        return 1, 1
    return (1, 0) if elo_diff > 0 else (0, 1)

def draw_hunter_strategy(home_team, away_team, **_):
    """Widens the draw zone to Elo gap ≤ 150 (from 50).
    Capitalises on users under-betting draws (17% bets vs ~28% real rate)."""
    home = normalize_team(home_team)
    away = normalize_team(away_team)
    elo_diff = TEAM_RATINGS[home][0] - TEAM_RATINGS[away][0]
    if abs(elo_diff) <= 150:
        return 1, 1
    return (1, 0) if elo_diff > 0 else (0, 1)

def crowd_consensus_strategy(home_team, away_team, match_bets=None, **_):
    """Predict whatever the plurality of users bet for this match."""
    if not match_bets:
        return lean_low_strategy(home_team, away_team)
    from collections import Counter
    return Counter(match_bets).most_common(1)[0][0]

def crowd_contrarian_strategy(home_team, away_team, match_bets=None, **_):
    """Among the top-8 most likely Poisson scorelines, pick the one that
    fewest users predicted — maximises payoff when others miss."""
    home = normalize_team(home_team)
    away = normalize_team(away_team)
    lambda_home, lambda_away = calculate_lambdas(home, away)

    candidates = sorted(
        [((h, a), poisson(h, lambda_home) * poisson(a, lambda_away))
         for h in range(7) for a in range(7)],
        key=lambda x: -x[1]
    )
    top = [score for score, _ in candidates[:8]]

    if not match_bets:
        return top[0]

    from collections import Counter
    crowd = Counter(match_bets)
    return min(top, key=lambda s: crowd.get(s, 0))

# ---------------------------------------------------------------------------
# Strategy registry
# ---------------------------------------------------------------------------

STRATEGIES = [
    ("1x0",                elo_1x0_strategy),
    ("2x1",                elo_2x1_strategy),
    ("draw/1x0",           elo_1x0_draw_strategy),
    ("elo bolão",          elo_bolao_strategy),
    ("elo tiered",         elo_tiered_strategy),
    ("best expected",      best_expected_points_strategy),
    ("rating",             rating_strategy),
    # new strategies
    ("lean low",           lean_low_strategy),
    ("draw hunter",        draw_hunter_strategy),
    ("crowd consensus",    crowd_consensus_strategy),
    ("crowd contrarian",   crowd_contrarian_strategy),
]

# ---------------------------------------------------------------------------
# Execution helpers
# ---------------------------------------------------------------------------

SCORE_KEYS = ["pts", "pts_ctr", "pts_ctr_res", "pts_lin", "pts_lin_res"]

def load_data():
    users_df = pd.read_csv("users.csv")
    users = {int(r["id"]): r["user_name"] for _, r in users_df.iterrows()}

    bets_df = pd.read_csv("bet.csv")
    bets = {
        (int(r["user_id"]), int(r["match_id"])): (int(r["home_goals"]), int(r["away_goals"]))
        for _, r in bets_df.iterrows()
    }
    print(f"Loaded {len(bets)} bets from {len(users)} users")

    fixtures_df = pd.read_csv("fixtures.csv").dropna(subset=["final_home_goals", "final_away_goals"])
    fixtures_df = fixtures_df[
        (fixtures_df["final_home_goals"].astype(str) != "NULL") &
        (fixtures_df["final_away_goals"].astype(str) != "NULL")
    ].copy()
    fixtures_list = fixtures_df.to_dict("records")
    print(f"Loaded {len(fixtures_list)} finished matches from fixtures.csv")

    bets_by_match = {}
    for (uid, mid), score in bets.items():
        bets_by_match.setdefault(mid, []).append(score)

    return users, bets, bets_by_match, fixtures_list


def make_detail_row(player_name, phase, home, away, rh, ra, ph, pa, scores, match_bets):
    """Build one bets_detail row with all scoring methods and rarity stats."""
    pct_score, pct_res = _pcts(ph, pa, match_bets) if match_bets else (1.0, 1.0)
    pts = scores["pts"]
    return {
        "player":                  player_name,
        "phase":                   phase,
        "home":                    home,
        "away":                    away,
        "real_result":             f"{rh}x{ra}",
        "bet_result":              f"{ph}x{pa}",
        "pts":                     pts,
        "pct_bets_score":          round(pct_score * 100, 2),
        "mult_sqrt_score":         round(1 / math.sqrt(pct_score) if pts > 0 else 1.0, 4),
        "pts_contrarian_score":    scores["pts_ctr"],
        "mult_linear_score":       round(1 / pct_score if pts > 0 else 1.0, 4),
        "pts_linear_score":        scores["pts_lin"],
        "pct_bets_result":         round(pct_res * 100, 2),
        "mult_sqrt_result":        round(1 / math.sqrt(pct_res) if pts > 0 else 1.0, 4),
        "pts_contrarian_result":   scores["pts_ctr_res"],
        "mult_linear_result":      round(1 / pct_res if pts > 0 else 1.0, 4),
        "pts_linear_result":       scores["pts_lin_res"],
    }


def score_all_matches(fixtures_list, bets, bets_by_match, users):
    """Score every finished match for all strategies and users.

    Returns (match_rows, detail_rows, strategy_totals, user_totals, max_possible).
    strategy_totals[name][key] and user_totals[uid][key] for key in SCORE_KEYS.
    """
    match_rows       = []
    detail_rows      = []
    strategy_totals  = {name: {k: 0.0 for k in SCORE_KEYS} for name, _ in STRATEGIES}
    user_totals      = {uid:  {k: 0.0 for k in SCORE_KEYS} for uid in users}
    max_possible     = 0

    for f in fixtures_list:
        match_id   = f["id"]
        phase      = f.get("phase")
        home       = normalize_team(f["home"])
        away       = normalize_team(f["away"])
        rh         = int(f["final_home_goals"])
        ra         = int(f["final_away_goals"])
        max_possible += 6 * get_phase_multiplier(phase)
        match_bets = bets_by_match.get(match_id, [])

        row = {"match_id": match_id, "phase": phase, "home": home, "away": away,
               "result": f"{rh}x{ra}"}

        for name, fn in STRATEGIES:
            ph, pa = fn(home, away, match_bets=match_bets)
            sc = score_prediction(ph, pa, rh, ra, phase, match_bets)
            for k in SCORE_KEYS:
                row[f"strat_{name}_{k}"] = sc[k]
                strategy_totals[name][k] += sc[k]
            detail_rows.append(make_detail_row(
                "estratégia: " + name, phase, home, away, rh, ra, ph, pa, sc, match_bets
            ))

        for uid in users:
            bet = bets.get((uid, match_id))
            if bet is not None:
                bh, ba = bet
                sc = score_prediction(bh, ba, rh, ra, phase, match_bets)
                detail_rows.append(make_detail_row(
                    users[uid], phase, home, away, rh, ra, bh, ba, sc, match_bets
                ))
            else:
                sc = {k: 0.0 for k in SCORE_KEYS}
            for k in SCORE_KEYS:
                row[f"user_{uid}_{k}"] = sc[k]
                user_totals[uid][k] += sc[k]

        match_rows.append(row)

    return match_rows, detail_rows, strategy_totals, user_totals, max_possible


def build_ranking_rows(users, user_totals, strategy_totals):
    """Build a flat list of dicts suitable for ranking DataFrames."""
    rows = []
    for uid, uname in users.items():
        t = user_totals[uid]
        rows.append({
            "participant":       uname,
            "type":              "jogador",
            "total_pts":         t["pts"],
            "total_pts_ctr":     round(t["pts_ctr"], 2),
            "total_pts_ctr_res": round(t["pts_ctr_res"], 2),
            "total_pts_lin":     round(t["pts_lin"], 2),
            "total_pts_lin_res": round(t["pts_lin_res"], 2),
        })
    for sname, t in strategy_totals.items():
        rows.append({
            "participant":       sname,
            "type":              "estratégia",
            "total_pts":         t["pts"],
            "total_pts_ctr":     round(t["pts_ctr"], 2),
            "total_pts_ctr_res": round(t["pts_ctr_res"], 2),
            "total_pts_lin":     round(t["pts_lin"], 2),
            "total_pts_lin_res": round(t["pts_lin_res"], 2),
        })
    return rows


RANKINGS = [
    ("total_pts",         "ranking.csv",                    "=== Ranking por pontos normais ==="),
    ("total_pts_ctr",     "ranking_ctr_score.csv",          "=== Contrarian placar 1/√pct ==="),
    ("total_pts_ctr_res", "ranking_ctr_result.csv",         "=== Contrarian resultado 1/√pct ==="),
    ("total_pts_lin",     "ranking_linear_score.csv",       "=== Linear placar 1/pct ==="),
    ("total_pts_lin_res", "ranking_linear_result.csv",      "=== Linear resultado 1/pct ==="),
]


def save_rankings(ranking_rows):
    for col, filename, label in RANKINGS:
        df = (
            pd.DataFrame(ranking_rows)
            .sort_values(col, ascending=False)
            .reset_index(drop=True)
        )
        df.index += 1
        df.index.name = "pos"
        df.to_csv(filename)
        print(f"\n{label}")
        print(df[["participant", "type", col]].to_string())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    users, bets, bets_by_match, fixtures_list = load_data()

    match_rows, detail_rows, strategy_totals, user_totals, max_possible = \
        score_all_matches(fixtures_list, bets, bets_by_match, users)

    pd.DataFrame(match_rows).to_csv("results.csv", index=False)
    pd.DataFrame(detail_rows).to_csv("bets_detail.csv", index=False)
    print(f"Saved bets_detail.csv ({len(detail_rows)} rows)")

    ranking_rows = build_ranking_rows(users, user_totals, strategy_totals)
    save_rankings(ranking_rows)

    print(f"\nMáx possível: {max_possible} pts  |  {len(fixtures_list)} jogos encerrados")


if __name__ == "__main__":
    main()