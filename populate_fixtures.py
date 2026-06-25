import os
import requests
from datetime import date, timedelta

API_TOKEN = os.getenv("FOOTBALL_DATA_TOKEN")  # set this in Render/env
BASE_URL = "https://api.football-data.org/v4"

headers = {
    "X-Auth-Token": "e0ee125088694e0799a6ed7d23ccfc1c"
}

def get_world_cup_matches(date_from=None, date_to=None, status=None):
    url = f"{BASE_URL}/competitions/WC/matches"

    params = {}
    if status:
        params["status"] = status  # FINISHED, LIVE, IN_PLAY, PAUSED, TIMED, SCHEDULED

    response = requests.get(url, headers=headers, params=params, timeout=20)
    response.raise_for_status()

    return response.json()["matches"]


def parse_match(match):
    score = match.get("score", {})
    full_time = score.get("fullTime", {})

    return {
        "api_fixture_id": match["id"],
        "utc_date": match["utcDate"],
        "status": match["status"],
        "home_team": match["homeTeam"]["name"],
        "away_team": match["awayTeam"]["name"],
        "home_goals": full_time.get("home"),
        "away_goals": full_time.get("away"),
        "stage": match.get("stage"),
        "group": match.get("group"),
        "last_updated": match.get("lastUpdated"),
    }


# Example: get yesterday + today + tomorrow
today = date.today()
matches = get_world_cup_matches(
    date_from=(today - timedelta(days=1)).isoformat(),
    date_to=(today + timedelta(days=1)).isoformat()
)

for match in matches:
    print(parse_match(match))