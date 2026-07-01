import pandas as pd

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

def normalize_team(team):
    team = str(team).strip()
    return ALIASES.get(team, team)

def get_result(home_goals, away_goals):
    if home_goals > away_goals:
        return "H"
    elif home_goals < away_goals:
        return "A"
    else:
        return "D"

def calculate_points(pred_home, pred_away, real_home, real_away):
    pred_result = get_result(pred_home, pred_away)
    real_result = get_result(real_home, real_away)

    if pred_home == real_home and pred_away == real_away:
        return 6

    if pred_result == real_result:
        if pred_result == "D":
            return 3
        elif (pred_home - pred_away) == (real_home - real_away):
            return 4
        else:
            return 2

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

    pred_home_1, pred_away_1 = elo_1x0_strategy(home, away)
    pred_home_2, pred_away_2 = elo_2x1_strategy(home, away)
    pred_home_3, pred_away_3 = elo_1x0_draw_strategy(home, away)

    points_1 = calculate_points(pred_home_1, pred_away_1, real_home, real_away)
    points_2 = calculate_points(pred_home_2, pred_away_2, real_home, real_away)
    points_3 = calculate_points(pred_home_3, pred_away_3, real_home, real_away)

    rows.append({
        "match_id": match.get("id", None),
        "home": home,
        "away": away,
        "home_elo": TEAM_RATINGS[home][0],
        "away_elo": TEAM_RATINGS[away][0],
        "elo_favorite": home if TEAM_RATINGS[home][0] >= TEAM_RATINGS[away][0] else away,
        "actual": f"{real_home}-{real_away}",
        "points 1x0": points_1,
        "points 2x1": points_2,
        "points draw 1x0": points_3,

    })

results = pd.DataFrame(rows)

print("Total points 1x0:", results["points 1x0"].sum())
print("% 1x0:", round(results["points 1x0"].sum() / (len(results) * 6) * 100, 0), "%")
print("")
print("Total points 2x1:", results["points 2x1"].sum())
print("% 2x1:", round(results["points 2x1"].sum() / (len(results) * 6) * 100, 0), "%")
print("")
print("Total points Draw 1x0:", results["points draw 1x0"].sum())
print("% Draw 1x0:", round(results["points draw 1x0"].sum() / (len(results) * 6) * 100, 0), "%")