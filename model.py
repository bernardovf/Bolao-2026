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

def elo_1x0_strategy(home_team, away_team):
    home = normalize_team(home_team)
    away = normalize_team(away_team)

    home_elo = TEAM_RATINGS[home][0]
    away_elo = TEAM_RATINGS[away][0]

    if home_elo >= away_elo:
        return 1, 0
    else:
        return 0, 1

def elo_2x1_strategy(home_team, away_team):
    home = normalize_team(home_team)
    away = normalize_team(away_team)

    home_elo = TEAM_RATINGS[home][0]
    away_elo = TEAM_RATINGS[away][0]

    if home_elo >= away_elo:
        return 2, 1
    else:
        return 1, 2

def elo_1x0_draw_strategy(home_team, away_team):
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

def elo_bolao_strategy(home_team, away_team):
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

def elo_tiered_strategy(home_team, away_team):
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

def best_expected_points_strategy(home_team, away_team, max_goals=6):
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

def rating_strategy(home_team, away_team):
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

# Read file
fixtures = pd.read_csv("fixtures.csv")

# Keep only matches with final scores
fixtures = fixtures.dropna(subset=["final_home_goals", "final_away_goals"]).copy()

fixtures["final_home_goals"] = fixtures["final_home_goals"].astype(int)
fixtures["final_away_goals"] = fixtures["final_away_goals"].astype(int)

rows = []

for _, match in fixtures.iterrows():
    home = normalize_team(match["home"])
    away = normalize_team(match["away"])
    real_home = int(match["final_home_goals"])
    real_away = int(match["final_away_goals"])
    phase = match.get("phase")
    multiplier = get_phase_multiplier(phase)

    pred_home_1, pred_away_1 = elo_1x0_strategy(home, away)
    pred_home_2, pred_away_2 = elo_2x1_strategy(home, away)
    pred_home_3, pred_away_3 = elo_1x0_draw_strategy(home, away)
    pred_home_4, pred_away_4 = elo_bolao_strategy(home, away)
    pred_home_5, pred_away_5 = elo_tiered_strategy(home, away)
    pred_home_6, pred_away_6 = best_expected_points_strategy(home, away)
    pred_home_7, pred_away_7 = rating_strategy(home, away)

    points_1 = calculate_points(pred_home_1, pred_away_1, real_home, real_away, phase)
    points_2 = calculate_points(pred_home_2, pred_away_2, real_home, real_away, phase)
    points_3 = calculate_points(pred_home_3, pred_away_3, real_home, real_away, phase)
    points_4 = calculate_points(pred_home_4, pred_away_4, real_home, real_away, phase)
    points_5 = calculate_points(pred_home_5, pred_away_5, real_home, real_away, phase)
    points_6 = calculate_points(pred_home_6, pred_away_6, real_home, real_away, phase)
    points_7 = calculate_points(pred_home_7, pred_away_7, real_home, real_away, phase)

    rows.append({
        "match_id": match.get("id", None),
        "phase": phase,
        "multiplier": multiplier,
        "home": home,
        "away": away,
        "home_elo": TEAM_RATINGS[home][0],
        "away_elo": TEAM_RATINGS[away][0],
        "elo_favorite": home if TEAM_RATINGS[home][0] >= TEAM_RATINGS[away][0] else away,
        "actual": f"{real_home} x {real_away}",
        "points 1x0": points_1,
        "points 2x1": points_2,
        "points draw 1x0": points_3,
        "points just elo": points_4,
        "points elo tiered": points_5,
        "best expected": points_6,
        "rating strategy": points_7,
        "elo tiered": f"{pred_home_7} x {pred_away_7}",
    })

results = pd.DataFrame(rows)
results.to_csv("results.csv", index=False)

max_possible = (results["multiplier"] * 6).sum()

def pct(col):
    return round(results[col].sum() / max_possible * 100, 0)

print("Total points 1x0:", results["points 1x0"].sum())
print("% 1x0:", pct("points 1x0"), "%")
print("")
print("Total points 2x1:", results["points 2x1"].sum())
print("% 2x1:", pct("points 2x1"), "%")
print("")
print("Total points Draw 1x0:", results["points draw 1x0"].sum())
print("% Draw 1x0:", pct("points draw 1x0"), "%")
print("")
print("Total points elo:", results["points just elo"].sum())
print("% elo:", pct("points just elo"), "%")
print("")
print("Total points elo tiered:", results["points elo tiered"].sum())
print("% elo tiered:", pct("points elo tiered"), "%")
print("")
print("Total best expected:", results["best expected"].sum())
print("% best expected:", pct("best expected"), "%")
print("")
print("Total rating strategy:", results["rating strategy"].sum())
print("% rating strategy:", pct("rating strategy"), "%")