import pandas as pd
import unicodedata

TEAM_MAP = {
    "usa": "united states",
    "united states": "united states",

    "turkey": "turkiye",
    "türkiye": "turkiye",

    "ivory coast": "cote d'ivoire",
    "côte d'ivoire": "cote d'ivoire",

    "bosnia & herzegovina": "bosnia and herzegovina",
    "bosnia and herzegovina": "bosnia and herzegovina",

    "czech republic": "czechia",
    "czechia": "czechia",

    "korea republic": "south korea",
    "south korea": "south korea",

    "cape verde": "cabo verde",
    "cabo verde": "cabo verde",

    "dr congo": "democratic republic of the congo",
    "democratic republic of the congo": "democratic republic of the congo",

    "curacao": "curaçao",
    "curaçao": "curaçao",
}

def normalize_team(name):
    name = str(name).strip().lower()

    name = (
        unicodedata.normalize("NFKD", name)
        .encode("ascii", "ignore")
        .decode("utf-8")
    )

    name = (
        name.replace("&", " and ")
            .replace("-", " ")
            .replace(".", "")
            .replace("'", "")
    )

    name = " ".join(name.split())

    return TEAM_MAP.get(name, name)


def add_team_keys(df, home_col, away_col):
    df = df.copy()

    df["home_norm"] = df[home_col].apply(normalize_team)
    df["away_norm"] = df[away_col].apply(normalize_team)

    df["team_1"] = df[["home_norm", "away_norm"]].min(axis=1)
    df["team_2"] = df[["home_norm", "away_norm"]].max(axis=1)

    df["match_key"] = df["team_1"] + " x " + df["team_2"]

    return df

# Read odds file
odds = pd.read_excel("WorldCup2026.xlsx")

# Keep only what we need
odds = odds[["Home", "Away", "H-Avg", "D-Avg", "A-Avg",]]

# ==========================
# Load data
# ==========================
fixtures = pd.read_csv("fixtures.csv")
bets = pd.read_csv("bet.csv")
users = pd.read_csv("users.csv")

fixtures = add_team_keys(fixtures, "home", "away")
odds = add_team_keys(odds, "Home", "Away")

fixtures["home_norm"] = fixtures["home"].apply(normalize_team)
fixtures["away_norm"] = fixtures["away"].apply(normalize_team)

odds["home_norm"] = odds["Home"].apply(normalize_team)
odds["away_norm"] = odds["Away"].apply(normalize_team)

# ==========================
# Stage multipliers
# ==========================
STAGE_MULTIPLIERS = {
    "Group Stage": 1,
    "16 Avos Final": 3,
    "Oitavas de Final": 4
}

odds_to_merge = odds[
    [
        "match_key",
        "home_norm",
        "away_norm",
        "H-Avg",
        "D-Avg",
        "A-Avg",
    ]
].rename(columns={
    "home_norm": "odds_home_norm",
    "away_norm": "odds_away_norm",
})


fixtures = fixtures.merge(
    odds_to_merge,
    on="match_key",
    how="inner",
)

fixtures["odds_was_inverted"] = (
    (fixtures["home_norm"] == fixtures["odds_away_norm"])
    & (fixtures["away_norm"] == fixtures["odds_home_norm"])
)

fixtures["home_odds"] = fixtures["H-Avg"]
fixtures["draw_odds"] = fixtures["D-Avg"]
fixtures["away_odds"] = fixtures["A-Avg"]

fixtures.loc[fixtures["odds_was_inverted"], "home_odds"] = fixtures.loc[
    fixtures["odds_was_inverted"], "A-Avg"
]

fixtures.loc[fixtures["odds_was_inverted"], "away_odds"] = fixtures.loc[
    fixtures["odds_was_inverted"], "H-Avg"
]

# ==========================
# Calculate points
# ==========================
def calculate_points(pred_home, pred_away, real_home, real_away, stage):
    # Ignore matches without result
    if pd.isna(real_home) or pd.isna(real_away) or real_home == 'NULL' or real_away == 'NULL':
        return 0

    pred_home = int(pred_home)
    pred_away = int(pred_away)
    real_home = int(real_home)
    real_away = int(real_away)

    # Base score
    if pred_home == real_home and pred_away == real_away:
        points = 6
    elif (pred_home - pred_away) == 0 and (real_home - real_away) == 0:
        points = 3
    elif (pred_home - pred_away) == (real_home - real_away):
        points = 4
    elif ((pred_home > pred_away and real_home > real_away) or (pred_home < pred_away and real_home < real_away)):
        points = 2
    else:
        points = 0

    multiplier = STAGE_MULTIPLIERS.get(stage, 1)

    return points * multiplier

def calculate_goal_by_goal_points(pred_home, pred_away, real_home, real_away, stage=None,):
    if pd.isna(real_home) or pd.isna(real_away) or real_home == 'NULL' or real_away == 'NULL':
        return 0

    pred_home = int(pred_home)
    pred_away = int(pred_away)
    real_home = int(real_home)
    real_away = int(real_away)

    points = 0

    # 2 points for exact home goals
    if pred_home == real_home:
        points += 2
    # 2 points for exact away goals
    if pred_away == real_away:
        points += 2
    # 2 points for correct winner/draw
    if ((pred_home > pred_away and real_home > real_away)
        or (pred_home < pred_away and real_home < real_away)
        or (pred_home == pred_away and real_home == real_away)):
        points += 2

    multiplier = STAGE_MULTIPLIERS.get(stage, 1)

    return points * multiplier

def calculate_simple_points(pred_home, pred_away, real_home, real_away, stage):
    # Ignore matches without result
    if pd.isna(real_home) or pd.isna(real_away) or real_home == 'NULL' or real_away == 'NULL':
        return 0

    pred_home = int(pred_home)
    pred_away = int(pred_away)
    real_home = int(real_home)
    real_away = int(real_away)

    # Base score
    if pred_home == real_home and pred_away == real_away:
        points = 6
    elif ((pred_home > pred_away and real_home > real_away) or (pred_home < pred_away and real_home < real_away)):
        points = 3
    else:
        points = 0

    multiplier = STAGE_MULTIPLIERS.get(stage, 1)

    return points * multiplier

def calculate_distance_points(pred_home, pred_away, real_home, real_away, stage):
    # Ignore matches without result
    if pd.isna(real_home) or pd.isna(real_away) or real_home == 'NULL' or real_away == 'NULL':
        return 0

    pred_home = int(pred_home)
    pred_away = int(pred_away)
    real_home = int(real_home)
    real_away = int(real_away)

    MAX_POINTS = 6  # pontuação máxima, igual ao placar exato

    def result(h, a):
        if h > a:
            return 'home'
        elif h < a:
            return 'away'
        else:
            return 'draw'

    # Só pontua se acertou o resultado (vencedor ou empate)
    if result(pred_home, pred_away) != result(real_home, real_away):
        points = 0
    else:
        # Distância entre o palpite e o resultado real, gol a gol
        error = abs(pred_home - real_home) + abs(pred_away - real_away)
        points = max(MAX_POINTS - error, 0)

    multiplier = STAGE_MULTIPLIERS.get(stage, 1)

    return points * multiplier

def calculate_points_odds(pred_home, pred_away, real_home, real_away, stage, home_odds, draw_odds, away_odds,):
    if (
        pd.isna(real_home)
        or pd.isna(real_away)
        or real_home == "NULL"
        or real_away == "NULL"
    ):
        return 0

    pred_home = int(pred_home)
    pred_away = int(pred_away)
    real_home = int(real_home)
    real_away = int(real_away)

    # Base score
    if pred_home == real_home and pred_away == real_away:
        points = 6

    elif pred_home == pred_away and real_home == real_away:
        points = 3

    elif (pred_home - pred_away) == (real_home - real_away):
        points = 4

    elif (
        (pred_home > pred_away and real_home > real_away)
        or (pred_home < pred_away and real_home < real_away)
    ):
        points = 2

    else:
        points = 0

    # Stage multiplier
    stage_multiplier = STAGE_MULTIPLIERS.get(stage, 1)

    # Odds multiplier according to ACTUAL result
    if real_home > real_away:
        odds_multiplier = home_odds
    elif real_home < real_away:
        odds_multiplier = away_odds
    else:
        odds_multiplier = draw_odds

    if pd.isna(odds_multiplier):
        odds_multiplier = 1

    return points * stage_multiplier * odds_multiplier

def calculate_points_2(pred_home, pred_away, real_home, real_away, stage):
    # Ignore matches without result
    if pd.isna(real_home) or pd.isna(real_away) or real_home == 'NULL' or real_away == 'NULL':
        return 0

    pred_home = int(pred_home)
    pred_away = int(pred_away)
    real_home = int(real_home)
    real_away = int(real_away)
    if pred_home > pred_away:
        pred = "home"
    elif pred_home < pred_away:
        pred = "away"
    else:
        pred = "draw"

    if real_home > real_away:
        real = "home"
    elif real_home < real_away:
        real = "away"
    else:
        real = "draw"

    # Base score
    if pred_home == real_home and pred_away == real_away:
        points = 6
    elif pred == real and pred == "home" and pred_home == real_home:
        points = 5
    elif pred == real and pred == "away" and pred_away == real_away:
        points = 5
    elif (pred_home - pred_away) == 0 and (real_home - real_away) == 0:
        points = 4
    elif pred == real and pred == "away" and pred_home == real_home:
        points = 3
    elif pred == real and pred == "home" and pred_away == real_away:
        points = 3
    elif pred == real:
        points = 2
    else:
        points = 0

    multiplier = STAGE_MULTIPLIERS.get(stage, 1)

    return points * multiplier


merged_odds = bets.merge(fixtures[["id", "final_home_goals", "final_away_goals", "phase", "home_odds", "draw_odds", "away_odds"]],
    left_on="match_id",
    right_on="id",
    how="inner",)
merged_odds["points"] = merged_odds.apply(lambda row: calculate_points_odds(
        row["home_goals"],
        row["away_goals"],
        row["final_home_goals"],
        row["final_away_goals"],
        row["phase"],
        row["home_odds"],
        row["draw_odds"],
        row["away_odds"],
    ), axis=1)
ranking = (merged_odds.groupby("user_id")["points"].sum().reset_index())
ranking = ranking.merge(users[["id", "user_name"]], left_on="user_id", right_on="id")
ranking = ranking.sort_values(by="points", ascending=False).reset_index(drop=True)
ranking["rank"] = ranking.index + 1
ranking = ranking[["rank", "user_name", "points"]]
print(ranking)
print("")

merged_simple = bets.merge(fixtures[["id", "final_home_goals", "final_away_goals", "phase", "home_odds", "draw_odds", "away_odds"]],
    left_on="match_id",
    right_on="id",
    how="inner",)
merged_simple["points"] = merged_simple.apply(lambda row: calculate_points_2(
        row["home_goals"],
        row["away_goals"],
        row["final_home_goals"],
        row["final_away_goals"],
        row["phase"]
    ), axis=1)
ranking = (merged_simple.groupby("user_id")["points"].sum().reset_index())
ranking = ranking.merge(users[["id", "user_name"]], left_on="user_id", right_on="id")
ranking = ranking.sort_values(by="points", ascending=False).reset_index(drop=True)
ranking["rank"] = ranking.index + 1
ranking = ranking[["rank", "user_name", "points"]]
print(ranking)


# Optional
